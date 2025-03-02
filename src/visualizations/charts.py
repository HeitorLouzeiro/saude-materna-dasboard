"""
Funções para criação de gráficos e visualizações
"""
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import seaborn as sns
import streamlit as st

from ..config import INDICADORES


def plot_stats(df_filtrado, indicador_selecionado):
    """
    Exibe estatísticas descritivas do indicador selecionado.

    Args:
        df_filtrado (pandas.DataFrame): DataFrame filtrado
        indicador_selecionado (str): Nome do indicador
    """
    media = df_filtrado[indicador_selecionado].mean()
    mediana = df_filtrado[indicador_selecionado].median()
    desvio = df_filtrado[indicador_selecionado].std()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Média", f"{media:.2f}%")
    with col2:
        st.metric("Mediana", f"{mediana:.2f}%")
    with col3:
        st.metric("Desvio Padrão", f"{desvio:.2f}")


def plot_macro_distribution(df_filtrado, indicador_selecionado):
    """
    Cria gráfico de barras da distribuição por macro-região.

    Args:
        df_filtrado (pandas.DataFrame): DataFrame filtrado
        indicador_selecionado (str): Nome do indicador
    """
    dados_macro = df_filtrado.groupby(
        'Macro')[indicador_selecionado].mean().reset_index()

    fig = go.Figure(data=[
        go.Bar(
            x=dados_macro["Macro"],
            y=dados_macro[indicador_selecionado],
            marker=dict(color='skyblue'),
            text=dados_macro[indicador_selecionado].round(2),
            textposition='outside'
        )
    ])

    fig.update_layout(
        title=f"Média por Macro-região - {INDICADORES[indicador_selecionado]}",
        xaxis_title="Macro-região",
        yaxis_title="Valor (%)",
        xaxis_tickangle=-45
    )

    st.plotly_chart(fig, use_container_width=True)


def plot_heatmap(df_filtrado, indicador_selecionado):
    """
    Cria mapa de calor por regional.

    Args:
        df_filtrado (pandas.DataFrame): DataFrame filtrado
        indicador_selecionado (str): Nome do indicador
    """
    dados_regional = df_filtrado.pivot_table(
        values=indicador_selecionado,
        index='Regional',
        columns='ANO',
        aggfunc='mean'
    )

    fig = plt.figure(figsize=(12, 8))
    sns.heatmap(dados_regional, cmap='YlOrRd', annot=True, fmt='.1f')
    plt.title(
        f"Distribuição por Regional - {INDICADORES[indicador_selecionado]}"
    )
    st.pyplot(fig)
    plt.close()


def plot_timeline(df_filtrado, indicador_selecionado):
    """
    Cria gráfico de linha do tempo.

    Args:
        df_filtrado (pandas.DataFrame): DataFrame filtrado
        indicador_selecionado (str): Nome do indicador
    """
    dados_tempo = df_filtrado.groupby(
        "ANO")[indicador_selecionado].mean().reset_index()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=dados_tempo["ANO"],
            y=dados_tempo[indicador_selecionado],
            mode="lines+markers",
            line=dict(color="blue", width=2),
            marker=dict(size=8, color="red")
        )
    )

    fig.update_layout(
        title=f"Evolução do Indicador: {INDICADORES[indicador_selecionado]}",
        xaxis_title="Ano",
        yaxis_title="Valor (%)",
        xaxis=dict(tickmode="linear"),
        yaxis=dict(showgrid=True)
    )

    st.plotly_chart(fig, use_container_width=True)


def plot_pie_chart(df_filtrado, indicador_selecionado):
    """
    Cria gráfico de pizza por regional.

    Args:
        df_filtrado (pandas.DataFrame): DataFrame filtrado
        indicador_selecionado (str): Nome do indicador
    """
    dados_pizza = df_filtrado.groupby(
        "Regional")[indicador_selecionado].sum().reset_index()

    fig = go.Figure(
        data=[
            go.Pie(
                labels=dados_pizza["Regional"],
                values=dados_pizza[indicador_selecionado],
                hole=0.3,
                textinfo="percent+label"
            )
        ]
    )

    fig.update_layout(title="Proporção do Indicador por Regional")
    st.plotly_chart(fig, use_container_width=True)


def plot_histogram(df_filtrado, indicador_selecionado):
    """
    Cria histograma da distribuição dos indicadores.

    Args:
        df_filtrado (pandas.DataFrame): DataFrame filtrado
        indicador_selecionado (str): Nome do indicador
    """
    # Reduzindo o tamanho da figura para 4x4
    fig = plt.figure(figsize=(4, 4))
    sns.histplot(
        df_filtrado[indicador_selecionado],
        bins=20,
        kde=True,
        color="royalblue"
    )

    plt.title(
        f"Distribuição do Indicador - {INDICADORES[indicador_selecionado]}"
    )
    plt.xlabel("Valor (%)")
    plt.ylabel("Frequência")

    st.pyplot(fig)
    plt.close()
