"""
Utilitários para criação e manipulação de mapas
"""
import pandas as pd


def get_coordinates_data(df):
    """
    Obtém as coordenadas das macrorregiões.

    Args:
        df (pandas.DataFrame): DataFrame com os dados

    Returns:
        dict: Dicionário com coordenadas e informações das macrorregiões
    """
    # Obter coordenadas das macrorregiões
    coordenadas_df = df[['Macro', 'LAT_RES', 'LON_RES', 'MUN']]

    # Obter lista única de municípios por macrorregião
    municipios_por_macro = (df.groupby('Macro')['MUN']
                            .agg(lambda x: '<br>'.join(sorted(set(x))))
                            .to_dict())

    # Criar dicionário de coordenadas
    coordenadas = {}
    for _, row in coordenadas_df.drop_duplicates('MUN').iterrows():
        coordenadas[row['Macro']] = {
            'lat': row['LAT_RES'],
            'lon': row['LON_RES'],
            'mun_ref': row['MUN'],
            'municipios': municipios_por_macro.get(row['Macro'], '')
        }

    return coordenadas


def calculate_connection_style(valor_origem, valor_destino):
    """
    Calcula o estilo da conexão entre duas macrorregiões.

    Args:
        valor_origem (float): Valor do indicador na origem
        valor_destino (float): Valor do indicador no destino

    Returns:
        tuple: (cor, largura) da linha de conexão
    """
    valor_medio = (valor_origem + valor_destino) / 2
    cor = f'rgba(255, {max(0, 255-valor_medio*2)}, 0, 0.5)'
    largura = max(1, min(5, valor_medio/20))

    return cor, largura


def get_macro_text(macro, coord, macro_selecionada):
    """
    Gera o texto de informação para uma macrorregião.

    Args:
        macro (str): Nome da macrorregião
        coord (dict): Dicionário com informações da macrorregião
        macro_selecionada (str): Macrorregião atualmente selecionada

    Returns:
        str: Texto formatado para exibição
    """
    if macro_selecionada != "Todas" and macro == macro_selecionada:
        return (f"{macro} - {coord['mun_ref']}<br>"
                f"Municípios:<br>{coord['municipios']}")
    return f"{macro} - {coord['mun_ref']}"
