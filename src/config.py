"""
Configurações globais para o dashboard de Saúde Materna
"""

# Configuração da página
PAGE_CONFIG = {
    "page_title": "Dashboard de Vigilância de Saúde Materna",
    "layout": "wide"
}

# Dicionário de indicadores
INDICADORES = {
    'IN1(6 CONSULTAS)': 'Consultas de pré-natal',
    'IN2 (HIV/SÍFILIS)': 'Testagem HIV/Sífilis',
    'IN3 (NV 6 CON)': 'Nascidos vivos com 6+ consultas',
    'IN4(PARTOS_CES)': 'Partos cesáreos',
    'IN5Q1 (RMM)': 'Razão de mortalidade materna'
}

# Configurações do mapa
MAP_CONFIG = {
    'scope': 'south america',
    'projection_type': 'mercator',
    'center_lon': -42,
    'center_lat': -6,
    'lat_range': [-12, 0],
    'lon_range': [-48, -36]
}

# Configurações de visualização
PLOT_CONFIG = {
    'default_height': 600,
    'default_width': None,  # None para usar container_width=True
    'color_scheme': 'YlOrRd'
}

# Caminho para o arquivo de dados
DATA_PATH = 'data/IndicadoresConsolidados_SaudeMaterna_empilhado.xlsx'
