"""
Aplicação principal do Dashboard de Vigilância de Saúde Materna
"""
import streamlit as st

from src.config import INDICADORES, PAGE_CONFIG
from src.data.loader import (filter_data, get_available_macros,
                             get_available_regionals, get_available_years,
                             load_data)
from src.visualizations.charts import (plot_heatmap, plot_histogram,
                                       plot_macro_distribution, plot_pie_chart,
                                       plot_stats, plot_timeline)
from src.visualizations.maps import criar_mapa_macrorregioes

# Configuração da página
st.set_page_config(**PAGE_CONFIG)

# Carregando os dados
df = load_data()

if df is None:
    st.stop()

# Título do dashboard
st.title("Dashboard de Vigilância de Saúde Materna")
st.markdown("---")

# Sidebar com filtros
st.sidebar.header("Filtros")

# Anos disponíveis
try:
    anos_disponiveis = get_available_years(df)
    ano_inicio, ano_fim = st.sidebar.slider(
        "Intervalo de anos",
        min_value=int(min(anos_disponiveis)),
        max_value=int(max(anos_disponiveis)),
        value=(int(min(anos_disponiveis)), int(max(anos_disponiveis)))
    )
except Exception as e:
    st.error(f"Erro ao processar os anos disponíveis: {str(e)}")
    st.stop()

# Seleção de Macro-região
macros = get_available_macros(df)
macro_selecionada = st.sidebar.selectbox(
    "Macro-região",
    ["Todas"] + list(macros)
)

# Seleção de Regional
regionais = get_available_regionals(df)
regional_selecionada = st.sidebar.selectbox(
    "Regional",
    ["Todas"] + list(regionais)
)

# Seleção de Indicador
indicador_selecionado = st.sidebar.selectbox(
    "Indicador",
    list(INDICADORES.keys()),
    format_func=lambda x: INDICADORES[x]
)

# Filtrando dados
df_filtrado = filter_data(
    df,
    ano_inicio,
    ano_fim,
    macro_selecionada,
    regional_selecionada
)

# Verificar se há dados após a filtragem
if df_filtrado.empty:
    st.warning("Não há dados disponíveis para os filtros selecionados.")
    st.stop()

# Estatísticas descritivas
st.subheader("Estatísticas Descritivas")
try:
    plot_stats(df_filtrado, indicador_selecionado)
except Exception as e:
    st.error(f"Erro ao calcular estatísticas: {str(e)}")

# Gráfico de distribuição por Macro
st.markdown("---")
st.subheader("Distribuição por Macro-região")
try:
    plot_macro_distribution(df_filtrado, indicador_selecionado)
except Exception as e:
    st.error(f"Erro ao gerar gráfico de distribuição: {str(e)}")

# Mapa de calor por Regional
st.markdown("---")
st.subheader("Mapa de Calor por Regional")
try:
    plot_heatmap(df_filtrado, indicador_selecionado)
except Exception as e:
    st.error(f"Erro ao gerar mapa de calor: {str(e)}")

# Mapa das Macrorregiões
st.markdown("---")
st.subheader("Mapa das Macrorregiões")
try:
    fig_mapa = criar_mapa_macrorregioes(
        df_filtrado,
        indicador_selecionado,
        macro_selecionada
    )
    st.plotly_chart(fig_mapa, use_container_width=True)
except Exception as e:
    st.error(f"Erro ao gerar mapa das macrorregiões: {str(e)}")

# Linha do Tempo
st.markdown("---")
st.subheader("Linha do Tempo - Evolução do Indicador")
try:
    plot_timeline(df_filtrado, indicador_selecionado)
except Exception as e:
    st.error(f"Erro ao gerar gráfico de linha do tempo: {str(e)}")

# Gráfico de Pizza por Regional
st.markdown("---")
st.subheader("Proporção do Indicador por Regional")
try:
    plot_pie_chart(df_filtrado, indicador_selecionado)
except Exception as e:
    st.error(f"Erro ao gerar gráfico de pizza: {str(e)}")

# Histograma
st.markdown("---")
st.subheader("Histograma - Distribuição dos Indicadores")
try:
    plot_histogram(df_filtrado, indicador_selecionado)
except Exception as e:
    st.error(f"Erro ao gerar histograma: {str(e)}")

# Rodapé com informações
st.markdown("---")
st.markdown("""
    **Fonte dos dados:** Fiocruz
    
    **Observações:**
    - Os dados apresentados são calculados com base nos registros oficiais
    - Os valores são atualizados conforme a disponibilidade dos dados
""")

# Informações sobre o indicador selecionado
st.sidebar.markdown("---")
st.sidebar.markdown("### Informações do Indicador")
st.sidebar.markdown(f"""
    **Indicador Selecionado:**
    {INDICADORES[indicador_selecionado]}

    **Período:**
    {ano_inicio} - {ano_fim}

    **Filtros Ativos:**
    - Macro: {macro_selecionada}
    - Regional: {regional_selecionada}
""")
