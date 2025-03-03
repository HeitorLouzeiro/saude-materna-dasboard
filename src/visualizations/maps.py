"""
Funções para criação e visualização de mapas
"""
import json

import folium
import pandas as pd

from ..config import INDICADORES


def criar_mapa_cobertura_consultas(caminho_excel="data/IndicadoresConsolidados_SaudeMaterna_empilhado.xlsx",
                                   caminho_geojson="data/geojs-22-mun.json",
                                   ano_inicio=None,
                                   ano_fim=None,
                                   macro_selecionada="Todas",
                                   regional_selecionada="Todas",
                                   indicador_selecionado="IN2 (HIV/SÍFILIS)"):
    """
    Cria um mapa interativo de cobertura de consultas usando Folium.

    Args:
        caminho_excel (str): Caminho para o arquivo Excel com os dados
        caminho_geojson (str): Caminho para o arquivo GeoJSON com os dados geográficos
        ano_inicio (int, optional): Ano inicial para filtrar os dados
        ano_fim (int, optional): Ano final para filtrar os dados
        macro_selecionada (str, optional): Macro-região selecionada para filtrar os dados
        regional_selecionada (str, optional): Regional selecionada para filtrar os dados
        indicador_selecionado (str, optional): Indicador selecionado para exibir no mapa

    Returns:
        tuple: (folium.Map, str) Retorna o objeto do mapa e o HTML do mapa
    """
    # 1️⃣ Carregar os dados
    df = pd.read_excel(caminho_excel, sheet_name=0)

    # 2️⃣ Obter anos únicos
    anos_disponiveis = sorted(df["ANO"].unique())

    # 3️⃣ Filtrar dados com base nos parâmetros
    if ano_inicio is not None and ano_fim is not None:
        df = df[(df["ANO"] >= ano_inicio) & (df["ANO"] <= ano_fim)]
    if macro_selecionada != "Todas":
        df = df[df["Macro"] == macro_selecionada]
    if regional_selecionada != "Todas":
        df = df[df["Regional"] == regional_selecionada]

    # 4️⃣ Carregar o GeoJSON
    with open(caminho_geojson, "r", encoding="utf-8") as f:
        geojson_data = json.load(f)

    # 5️⃣ Criar o mapa base
    mapa = folium.Map(location=[-7.7183, -42.7289], zoom_start=7)

    # 6️⃣ Criar camadas exclusivas para cada ano
    primeiro_ano = True  # Para ativar apenas a primeira camada
    for ano in anos_disponiveis:
        df_ano = df[df["ANO"] == ano]
        df_ano = df_ano[["MUN", indicador_selecionado]].fillna(0)

        # Criar um dicionário {Município: Valor}
        dados_municipios = df_ano.set_index(
            "MUN")[indicador_selecionado].to_dict()

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

        # Obter o nome amigável do indicador para exibição
        nome_indicador = INDICADORES.get(
            indicador_selecionado, indicador_selecionado)

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
                aliases=["Município", f"{nome_indicador} (%)"],
                labels=True
            )
        ).add_to(layer)

        layer.add_to(mapa)

        # Ativar apenas a primeira camada
        if primeiro_ano:
            mapa.add_child(layer)
            primeiro_ano = False

    # 7️⃣ Adicionar o LayerControl
    folium.LayerControl(collapsed=False).add_to(mapa)

    # Retornar tanto o mapa quanto o HTML
    return mapa, mapa._repr_html_()
