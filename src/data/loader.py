"""
Módulo para carregamento e processamento de dados
"""
import pandas as pd
import streamlit as st

from ..config import DATA_PATH


@st.cache_data
def load_data():
    """
    Carrega os dados do arquivo Excel e armazena em cache.

    Returns:
        pandas.DataFrame: DataFrame com os dados carregados ou None em caso de erro
    """
    try:
        df = pd.read_excel(DATA_PATH)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {str(e)}")
        return None


def filter_data(df, ano_inicio, ano_fim, macro_selecionada="Todas",
                regional_selecionada="Todas"):
    """
    Filtra os dados com base nos parâmetros fornecidos.

    Args:
        df (pandas.DataFrame): DataFrame original
        ano_inicio (int): Ano inicial do filtro
        ano_fim (int): Ano final do filtro
        macro_selecionada (str): Macro região selecionada
        regional_selecionada (str): Regional selecionada

    Returns:
        pandas.DataFrame: DataFrame filtrado
    """
    df_filtrado = df.copy()

    # Aplicando filtros
    df_filtrado = df_filtrado[df_filtrado['ANO'].between(ano_inicio, ano_fim)]

    if macro_selecionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado['Macro'] == macro_selecionada]

    if regional_selecionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado['Regional']
                                  == regional_selecionada]

    return df_filtrado


def get_available_years(df):
    """
    Retorna os anos disponíveis no DataFrame.

    Args:
        df (pandas.DataFrame): DataFrame com os dados

    Returns:
        list: Lista de anos disponíveis ordenados
    """
    return sorted(df['ANO'].unique())


def get_available_macros(df):
    """
    Retorna as macro regiões disponíveis no DataFrame.

    Args:
        df (pandas.DataFrame): DataFrame com os dados

    Returns:
        list: Lista de macro regiões ordenadas
    """
    return sorted(df['Macro'].unique())


def get_available_regionals(df):
    """
    Retorna as regionais disponíveis no DataFrame.

    Args:
        df (pandas.DataFrame): DataFrame com os dados

    Returns:
        list: Lista de regionais ordenadas
    """
    return sorted(df['Regional'].unique())
