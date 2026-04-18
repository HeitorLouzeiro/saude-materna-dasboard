"""
Aplicação principal do Dashboard de Vigilância de Saúde Materna
"""
import streamlit as st
import streamlit.components.v1 as components

from src.config import INDICADORES, PAGE_CONFIG, PLOT_CONFIG
from src.data.loader import (filter_data, get_available_macros,
                             get_available_regionals, get_available_years,
                             load_data)
from src.visualizations.charts import (plot_heatmap, plot_histogram,
                                       plot_macro_distribution, plot_pie_chart,
                                       plot_stats, plot_timeline)
from src.visualizations.maps import criar_mapa_cobertura_consultas

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
# Regional depende dos filtros de período e macro
# para evitar combinações vazias
df_base_regionais = df[df['ANO'].between(ano_inicio, ano_fim)]
if macro_selecionada != "Todas":
    df_base_regionais = df_base_regionais[
        df_base_regionais['Macro'] == macro_selecionada
    ]

regionais = get_available_regionals(df_base_regionais)
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

# Layout da seção comparativa para melhorar experiência em mobile
layout_comparativo = st.sidebar.radio(
    "Layout da seção comparativa",
    ["Automático", "Lado a lado", "Empilhado"],
    help=(
        "Automático usa abas (melhor em telas pequenas). "
        "Lado a lado prioriza desktop."
    )
)

altura_mapa = st.sidebar.slider(
    "Altura do mapa (px)",
    min_value=400,
    max_value=900,
    value=int(PLOT_CONFIG['default_height']),
    step=50
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


def run_safely(render_function, error_prefix):
    """Executa função de renderização com tratamento de erro padrão."""
    try:
        render_function()
    except Exception as e:
        st.error(f"{error_prefix}: {str(e)}")


# Estatísticas descritivas
st.subheader("Estatísticas Descritivas")
run_safely(
    lambda: plot_stats(df_filtrado, indicador_selecionado),
    "Erro ao calcular estatísticas"
)

# Gráfico de distribuição por Macro
st.markdown("---")
st.subheader("Distribuição por Macro-região")
run_safely(
    lambda: plot_macro_distribution(df_filtrado, indicador_selecionado),
    "Erro ao gerar gráfico de distribuição"
)

# Mapa de calor por Regional
st.markdown("---")
st.subheader("Mapa de Calor por Regional")
run_safely(
    lambda: plot_heatmap(df_filtrado, indicador_selecionado),
    "Erro ao gerar mapa de calor"
)

# Mapa das Macrorregiões - Folium
st.markdown("---")
st.subheader("Mapa das Macrorregiões")


def render_map_section():
    _, html_mapa = criar_mapa_cobertura_consultas(
        df_filtrado=df_filtrado,
        indicador_selecionado=indicador_selecionado
    )
    components.html(html_mapa, height=altura_mapa)


run_safely(
    render_map_section,
    "Erro ao gerar mapa das macrorregiões - Folium"
)

# Seção comparativa: linha do tempo e distribuição regional
st.markdown("---")


def render_timeline_section():
    st.subheader("Linha do Tempo - Evolução do Indicador")
    run_safely(
        lambda: plot_timeline(df_filtrado, indicador_selecionado),
        "Erro ao gerar gráfico de linha do tempo"
    )


def render_regional_section():
    st.subheader("Média do Indicador por Regional")
    run_safely(
        lambda: plot_pie_chart(df_filtrado, indicador_selecionado),
        "Erro ao gerar gráfico de pizza"
    )


if layout_comparativo == "Lado a lado":
    col1, col2 = st.columns(2)
    with col1:
        render_timeline_section()
    with col2:
        render_regional_section()
elif layout_comparativo == "Empilhado":
    render_timeline_section()
    render_regional_section()
else:
    tab_tempo, tab_regional = st.tabs([
        "Linha do Tempo",
        "Distribuição Regional"
    ])
    with tab_tempo:
        render_timeline_section()
    with tab_regional:
        render_regional_section()

# Histograma
st.markdown("---")
st.subheader("Histograma - Distribuição dos Indicadores")
run_safely(
    lambda: plot_histogram(df_filtrado, indicador_selecionado),
    "Erro ao gerar histograma"
)

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
