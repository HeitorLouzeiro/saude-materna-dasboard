"""
Funções para criação e visualização de mapas interativos
"""

import json
from functools import lru_cache

import branca
import folium
import pandas as pd

from ..config import DATA_PATH, GEOJSON_PATH, INDICADORES, PLOT_CONFIG


MAP_COLOR_SCALES = {
    "YlOrRd": branca.colormap.linear.YlOrRd_09,
    "YlGnBu": branca.colormap.linear.YlGnBu_09
}


@lru_cache(maxsize=2)
def _load_geojson(caminho_geojson):
    """Carrega e mantém o GeoJSON em cache para reduzir I/O."""
    with open(caminho_geojson, "r", encoding="utf-8") as geojson_file:
        return json.load(geojson_file)


def _build_colormap(valor_min, valor_max):
    """Cria colormap configurável e robusto para variação mínima."""
    colormap_name = PLOT_CONFIG.get("map_color_scheme", "YlOrRd")
    colormap_scale = MAP_COLOR_SCALES.get(
        colormap_name,
        branca.colormap.linear.YlOrRd_09
    )

    if valor_min == valor_max:
        valor_max = valor_min + 1

    return colormap_scale.scale(valor_min, valor_max).to_step(10)


def criar_mapa_cobertura_consultas(caminho_excel=DATA_PATH,
                                   caminho_geojson=GEOJSON_PATH,
                                   ano_inicio=None,
                                   ano_fim=None,
                                   macro_selecionada="Todas",
                                   regional_selecionada="Todas",
                                   indicador_selecionado="IN2 (HIV/SÍFILIS)",
                                   df_filtrado=None):
    """
    Cria um mapa interativo de cobertura de consultas usando Folium.

    Args:
        caminho_excel (str): Caminho para o arquivo Excel com os dados
        caminho_geojson (str): Caminho para o arquivo GeoJSON
            com os dados geográficos
        ano_inicio (int, optional): Ano inicial para filtrar os dados
        ano_fim (int, optional): Ano final para filtrar os dados
        macro_selecionada (str, optional): Macro-região selecionada
            para filtrar os dados
        regional_selecionada (str, optional): Regional selecionada
            para filtrar os dados
        indicador_selecionado (str, optional): Indicador selecionado
            para exibir no mapa
        df_filtrado (pandas.DataFrame, optional): DataFrame já filtrado para
            renderizar o mapa sem reler o arquivo Excel

    Returns:
        tuple: (folium.Map, str) Retorna o objeto do mapa e o HTML do mapa
    """

    # Usa DataFrame pré-filtrado quando disponível
    # para evitar releitura do Excel
    if df_filtrado is not None:
        df = df_filtrado.copy()
    else:
        df = pd.read_excel(caminho_excel, sheet_name=0)

        if ano_inicio is not None and ano_fim is not None:
            df = df[(df["ANO"] >= ano_inicio) & (df["ANO"] <= ano_fim)]
        if macro_selecionada != "Todas":
            df = df[df["Macro"] == macro_selecionada]
        if regional_selecionada != "Todas":
            df = df[df["Regional"] == regional_selecionada]

    # Verificar se a coluna "MUN" existe
    if "MUN" not in df.columns:
        raise ValueError("A coluna 'MUN' não foi encontrada no DataFrame.")

    if df.empty:
        raise ValueError("Não há dados disponíveis para gerar o mapa.")

    # Os anos devem refletir o estado já filtrado dos dados
    anos_disponiveis = sorted(df["ANO"].unique())

    # Carregar o GeoJSON
    geojson_data = _load_geojson(caminho_geojson)

    # Criar o mapa base
    mapa = folium.Map(location=[-7.7183, -42.7289], zoom_start=7, tiles=None)

    # Criar colormap para diferenciação de valores
    valores_indicador = df[indicador_selecionado].dropna()
    if valores_indicador.empty:
        raise ValueError("Não há valores numéricos para gerar o mapa.")

    colormap = _build_colormap(
        float(valores_indicador.min()),
        float(valores_indicador.max())
    )
    indicador_titulo = INDICADORES.get(
        indicador_selecionado,
        indicador_selecionado
    )
    colormap.caption = f"{indicador_titulo} (%)"
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
        def estilo(feature, dados_municipios=dados_municipios):
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
                    "Município",
                    f"{indicador_titulo} (%)"
                ],
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
