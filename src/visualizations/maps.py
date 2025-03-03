"""
Funções para criação e visualização de mapas
"""
import json

import folium
import pandas as pd
import plotly.graph_objects as go

from ..config import INDICADORES, MAP_CONFIG
from ..utils.map_utils import (calculate_connection_style,
                               get_coordinates_data, get_macro_text)


def criar_mapa_macrorregioes(df_filtrado, indicador_selecionado, macro_selecionada):
    """
    Cria o mapa interativo das macrorregiões.

    Args:
        df_filtrado (pandas.DataFrame): DataFrame filtrado
        indicador_selecionado (str): Nome do indicador
        macro_selecionada (str): Macrorregião selecionada

    Returns:
        plotly.graph_objects.Figure: Figura do mapa
    """
    coordenadas = get_coordinates_data(df_filtrado)

    fig = go.Figure()

    # Adicionar marcadores para cada macrorregião
    for macro, coord in coordenadas.items():
        texto = get_macro_text(macro, coord, macro_selecionada)

        fig.add_trace(go.Scattergeo(
            lon=[coord['lon']],
            lat=[coord['lat']],
            text=[texto],
            mode='markers+text',
            marker=dict(size=10, color='red'),
            textposition="bottom center",
            name='Macrorregiões',
            hoverinfo='text'
        ))

    # Adicionar conexões entre macrorregiões
    for i, origem in enumerate(coordenadas.keys()):
        for destino in list(coordenadas.keys())[i+1:]:
            valor_origem = df_filtrado[
                df_filtrado['Macro'] == origem
            ][indicador_selecionado].mean()

            valor_destino = df_filtrado[
                df_filtrado['Macro'] == destino
            ][indicador_selecionado].mean()

            cor, largura = calculate_connection_style(
                valor_origem, valor_destino)
            valor_medio = (valor_origem + valor_destino) / 2

            fig.add_trace(go.Scattergeo(
                lon=[coordenadas[origem]['lon'], coordenadas[destino]['lon']],
                lat=[coordenadas[origem]['lat'], coordenadas[destino]['lat']],
                mode='lines',
                line=dict(width=largura, color=cor),
                text=f"{origem} → {destino}: {valor_medio:.1f}%",
                hoverinfo='text',
                showlegend=False
            ))

    # Configurar layout do mapa
    fig.update_layout(
        title='Mapa de Distribuição - ' + INDICADORES[indicador_selecionado],
        geo=dict(
            scope=MAP_CONFIG['scope'],
            projection_type=MAP_CONFIG['projection_type'],
            showland=True,
            landcolor='rgb(243, 243, 243)',
            countrycolor='rgb(204, 204, 204)',
            center=dict(
                lon=MAP_CONFIG['center_lon'],
                lat=MAP_CONFIG['center_lat']
            ),
            lataxis_range=MAP_CONFIG['lat_range'],
            lonaxis_range=MAP_CONFIG['lon_range']
        ),
        height=600,
        margin=dict(l=0, r=0, t=30, b=0)
    )

    return fig


def criar_mapa_cobertura_consultas(caminho_excel="data/IndicadoresConsolidados_SaudeMaterna_empilhado.xlsx",
                                   caminho_geojson="data/geojs-22-mun.json"):
    """
    Cria um mapa interativo de cobertura de consultas usando Folium.

    Args:
        caminho_excel (str): Caminho para o arquivo Excel com os dados
        caminho_geojson (str): Caminho para o arquivo GeoJSON com os dados geográficos

    Returns:
        tuple: (folium.Map, str) Retorna o objeto do mapa e o HTML do mapa
    """
    # 1️⃣ Carregar os dados
    df = pd.read_excel(caminho_excel, sheet_name=0)

    # 2️⃣ Obter anos únicos
    anos_disponiveis = sorted(df["ANO"].unique())

    # 3️⃣ Carregar o GeoJSON
    with open(caminho_geojson, "r", encoding="utf-8") as f:
        geojson_data = json.load(f)

    # 4️⃣ Criar o mapa base
    mapa = folium.Map(location=[-7.7183, -42.7289], zoom_start=7)

    # 5️⃣ Criar camadas exclusivas para cada ano
    primeiro_ano = True  # Para ativar apenas a primeira camada
    for ano in anos_disponiveis:
        df_ano = df[df["ANO"] == ano]
        df_ano = df_ano[["MUN", "IN1(6 CONSULTAS)"]].fillna(0)

        # Criar um dicionário {Município: Valor}
        dados_municipios = df_ano.set_index(
            "MUN")["IN1(6 CONSULTAS)"].to_dict()

        # Função de estilo para colorir os municípios
        def estilo(feature):
            municipio = feature["properties"].get("name", "")
            valor = dados_municipios.get(municipio, "Sem dados")
            return {
                "fillColor": "blue" if valor != "Sem dados" else "gray",
                "color": "black",
                "fillOpacity": 0.6,
                "weight": 1
            }

        # Atualizar GeoJSON com os dados do ano
        for feature in geojson_data["features"]:
            municipio = feature["properties"].get("name", "")
            feature["properties"]["consulta"] = dados_municipios.get(
                municipio, "Sem dados")

        # Criar camada do ano (somente a primeira ativa)
        layer = folium.FeatureGroup(
            name=f"Ano {ano}", overlay=False, control=True)

        folium.GeoJson(
            geojson_data,
            style_function=estilo,
            highlight_function=lambda x: {
                "fillColor": "darkblue",
                "color": "black",
                "fillOpacity": 0.9,
                "weight": 2
            },
            tooltip=folium.GeoJsonTooltip(
                fields=["name", "consulta"],
                aliases=["Município", "Cobertura de 6 Consultas (%)"],
                labels=True
            )
        ).add_to(layer)

        layer.add_to(mapa)

        # Ativar apenas a primeira camada
        if primeiro_ano:
            mapa.add_child(layer)
            primeiro_ano = False

    # 6️⃣ Adicionar o LayerControl
    folium.LayerControl(collapsed=False).add_to(mapa)

    # Retornar tanto o mapa quanto o HTML
    return mapa, mapa._repr_html_()
