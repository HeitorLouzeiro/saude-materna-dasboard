"""
Funções para criação e visualização de mapas interativos
"""

import json

import branca
import folium
import pandas as pd

from ..config import DATA_PATH, GEOJSON_PATH, INDICADORES


def criar_mapa_cobertura_consultas(caminho_excel=DATA_PATH,
                                   caminho_geojson=GEOJSON_PATH,
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

    # Carregar os dados
    df = pd.read_excel(caminho_excel, sheet_name=0)

    # Verificar se a coluna "MUN" existe
    if "MUN" not in df.columns:
        raise ValueError("A coluna 'MUN' não foi encontrada no DataFrame.")

    # Obter anos disponíveis e filtrar
    anos_disponiveis = sorted(df["ANO"].unique())

    if ano_inicio is not None and ano_fim is not None:
        df = df[(df["ANO"] >= ano_inicio) & (df["ANO"] <= ano_fim)]
    if macro_selecionada != "Todas":
        df = df[df["Macro"] == macro_selecionada]
    if regional_selecionada != "Todas":
        df = df[df["Regional"] == regional_selecionada]

    # Carregar o GeoJSON
    with open(caminho_geojson, "r", encoding="utf-8") as f:
        geojson_data = json.load(f)

    # Criar o mapa base
    mapa = folium.Map(location=[-7.7183, -42.7289], zoom_start=7, tiles=None)

    # Criar colormap para diferenciação de valores
    colormap = branca.colormap.linear.YlGnBu_09.scale(
        min(df[indicador_selecionado]), max(df[indicador_selecionado])
    ).to_step(10)
    colormap.caption = f"{INDICADORES.get(indicador_selecionado, indicador_selecionado)} (%)"
    colormap.add_to(mapa)

    # Criar camadas exclusivas para cada ano
    primeiro_ano = True

    for ano in anos_disponiveis:
        df_ano = df[df["ANO"] == ano]
        df_ano = df_ano[["MUN", indicador_selecionado]].fillna(0)

        # Criar um dicionário {Município: Valor}
        dados_municipios = df_ano.set_index(
            "MUN")[indicador_selecionado].to_dict()

        # Criar uma cópia do GeoJSON
        geojson_copy = json.loads(json.dumps(geojson_data))

        # Atualizar GeoJSON com os dados do ano
        for feature in geojson_copy["features"]:
            municipio = feature["properties"].get("name", "")
            feature["properties"]["consulta"] = dados_municipios.get(
                municipio, "Sem dados")

        # Função de estilo com colormap
        def estilo(feature):
            municipio = feature["properties"].get("name", "")
            valor = dados_municipios.get(municipio, None)
            cor = colormap(valor) if isinstance(
                valor, (int, float)) else "gray"
            return {
                "fillColor": cor,
                "color": "black",
                "fillOpacity": 0.6,
                "weight": 1
            }

        # Criar camada para o ano
        layer = folium.FeatureGroup(
            name=f"Ano {ano}", overlay=False, control=True)

        folium.GeoJson(
            geojson_copy,
            style_function=estilo,
            highlight_function=lambda x: {
                "fillColor": "darkblue",
                "color": "black",
                "fillOpacity": 0.9,
                "weight": 2
            },
            tooltip=folium.GeoJsonTooltip(
                fields=["name", "consulta"],
                aliases=[
                    "Município", f"{INDICADORES.get(indicador_selecionado, indicador_selecionado)} (%)"],
                labels=True
            )
        ).add_to(layer)

        layer.add_to(mapa)

        if primeiro_ano:
            mapa.add_child(layer)
            primeiro_ano = False

    # Adicionar o LayerControl
    folium.LayerControl(collapsed=False).add_to(mapa)

    # Retornar mapa e HTML
    return mapa, mapa.get_root().render()
