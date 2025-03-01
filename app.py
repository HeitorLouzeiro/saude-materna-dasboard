import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Vigilância de Saúde Materna",
    layout="wide"
)

# Função para carregar e preparar os dados


@st.cache_data
def load_data():
    try:
        df = pd.read_excel(
            'data/IndicadoresConsolidados_SaudeMaterna_empilhado.xlsx'
        )
        return df
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {str(e)}")
        return None


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
    anos_disponiveis = sorted(df['ANO'].unique())
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
macros = sorted(df['Macro'].unique())
macro_selecionada = st.sidebar.selectbox(
    "Macro-região",
    ["Todas"] + list(macros)
)

# Seleção de Regional
regionais = sorted(df['Regional'].unique())
regional_selecionada = st.sidebar.selectbox(
    "Regional",
    ["Todas"] + list(regionais)
)

# Seleção de Indicador
indicadores = {
    'IN1(6 CONSULTAS)': 'Consultas de pré-natal',
    'IN2 (HIV/SÍFILIS)': 'Testagem HIV/Sífilis',
    'IN3 (NV 6 CON)': 'Nascidos vivos com 6+ consultas',
    'IN4(PARTOS_CES)': 'Partos cesáreos',
    'IN5Q1 (RMM)': 'Razão de mortalidade materna'
}

indicador_selecionado = st.sidebar.selectbox(
    "Indicador",
    list(indicadores.keys()),
    format_func=lambda x: indicadores[x]
)

# Filtrando dados
df_filtrado = df.copy()

# Aplicando filtros
df_filtrado = df_filtrado[df_filtrado['ANO'].between(ano_inicio, ano_fim)]

if macro_selecionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado['Macro'] == macro_selecionada]

if regional_selecionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado['Regional'] == regional_selecionada]

# Verificar se há dados após a filtragem
if df_filtrado.empty:
    st.warning("Não há dados disponíveis para os filtros selecionados.")
    st.stop()


_ = """
Este dashboard apresenta informações sobre os indicadores de saúde materna
Exemplo de uso:
Se estamos IN1(6 CONSULTAS) e queremos saber a média de consultas de pré-natal
por macro-região, podemos selecionar o indicador IN1(6 CONSULTAS) e filtrar
por Macro-região.

"""
# Estatísticas descritivas
st.subheader("Estatísticas Descritivas")
try:
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
except Exception as e:
    st.error(f"Erro ao calcular estatísticas: {str(e)}")

st.markdown("---")
# Gráfico de distribuição por Macro
st.subheader("Distribuição por Macro-região")
try:
    dados_macro = df_filtrado.groupby('Macro')[indicador_selecionado].mean()
    fig_macro = plt.figure(figsize=(10, 6))
    plt.bar(dados_macro.index, dados_macro.values)
    plt.title(
        f"Média por Macro-região - {indicadores[indicador_selecionado]}"
    )
    plt.xlabel("Macro-região")
    plt.ylabel("Valor (%)")
    plt.xticks(rotation=45)
    st.pyplot(fig_macro)
    plt.close()
except Exception as e:
    st.error(f"Erro ao gerar gráfico de distribuição: {str(e)}")


# Mapa de calor por Regional
st.markdown("---")
st.subheader("Mapa de Calor por Regional")
try:
    _ = """
    Pivot table para criar um mapa de calor com a média do indicador
    """
    dados_regional = df_filtrado.pivot_table(
        values=indicador_selecionado,
        index='Regional',
        columns='ANO',
        aggfunc='mean'
    )

    # Ordenar as colunas por ano
    fig_heatmap = plt.figure(figsize=(12, 8))

    # Gerar o mapa de calor com a média do indicador
    _ = """
    cmap: paleta de cores
    annot: exibir valores no mapa de calor
    fmt: formatação dos valores
    """
    sns.heatmap(dados_regional, cmap='YlOrRd', annot=True, fmt='.1f')
    plt.title(
        f"Distribuição por Regional - {indicadores[indicador_selecionado]}"
    )
    st.pyplot(fig_heatmap)
    plt.close()
except Exception as e:
    st.error(f"Erro ao gerar mapa de calor: {str(e)}")

# Rodapé com informações
st.markdown("---")
st.markdown("""
    **Fonte dos dados:** Ministério da Saúde
    
    **Observações:**
    - Os dados apresentados são calculados com base nos registros oficiais
    - Os valores são atualizados conforme a disponibilidade dos dados
""")

# Informações sobre o indicador selecionado
st.sidebar.markdown("---")
st.sidebar.markdown("### Informações do Indicador")
st.sidebar.markdown(f"""
    **Indicador Selecionado:**  
    {indicadores[indicador_selecionado]}
    
    **Período:**  
    {ano_inicio} - {ano_fim}
    
    **Filtros Ativos:**
    - Macro: {macro_selecionada}
    - Regional: {regional_selecionada}
""")
