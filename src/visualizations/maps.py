"""
Funções para criação e visualização de mapas
"""
import plotly.graph_objects as go
import streamlit as st

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
