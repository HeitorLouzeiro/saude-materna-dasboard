import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import seaborn as sns
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Vigilância de Saúde Materna",
    layout="wide"
)


def criar_mapa_macrorregioes(df_filtrado, indicador_selecionado):
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

    fig = go.Figure()

    # Adicionar marcadores para cada macrorregião
    for macro, coord in coordenadas.items():
        # Preparar texto com lista de municípios
        if macro_selecionada != "Todas" and macro == macro_selecionada:
            texto = (f"{macro} - {coord['mun_ref']}<br>"
                     f"Municípios:<br>{coord['municipios']}")
        else:
            texto = f"{macro} - {coord['mun_ref']}"

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

    fig.update_layout(
        title='Mapa de Distribuição - ' + indicadores[indicador_selecionado],
        geo=dict(
            scope='south america',
            projection_type='mercator',
            showland=True,
            landcolor='rgb(243, 243, 243)',
            countrycolor='rgb(204, 204, 204)',
            center=dict(lon=-42, lat=-6),
            lataxis_range=[-12, 0],
            lonaxis_range=[-48, -36]
        ),
        height=600,
        margin=dict(l=0, r=0, t=30, b=0)
    )

    # Adicionar conexões entre macrorregiões
    for i, origem in enumerate(coordenadas.keys()):
        for destino in list(coordenadas.keys())[i+1:]:
            valor_origem = df_filtrado[df_filtrado['Macro'] ==
                                       origem][indicador_selecionado].mean()
            valor_destino = df_filtrado[df_filtrado['Macro'] ==
                                        destino][indicador_selecionado].mean()
            valor_medio = (valor_origem + valor_destino) / 2

            cor = f'rgba(255, {max(0, 255-valor_medio*2)}, 0, 0.5)'
            largura = max(1, min(5, valor_medio/20))

            fig.add_trace(go.Scattergeo(
                lon=[coordenadas[origem]['lon'], coordenadas[destino]['lon']],
                lat=[coordenadas[origem]['lat'], coordenadas[destino]['lat']],
                mode='lines',
                line=dict(width=largura, color=cor),
                text=f"{origem} → {destino}: {valor_medio:.1f}%",
                hoverinfo='text',
                showlegend=False
            ))

    return fig


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
    dados_regional = df_filtrado.pivot_table(
        values=indicador_selecionado,
        index='Regional',
        columns='ANO',
        aggfunc='mean'
    )

    fig_heatmap = plt.figure(figsize=(12, 8))
    sns.heatmap(dados_regional, cmap='YlOrRd', annot=True, fmt='.1f')
    plt.title(
        f"Distribuição por Regional - {indicadores[indicador_selecionado]}"
    )
    st.pyplot(fig_heatmap)
    plt.close()
except Exception as e:
    st.error(f"Erro ao gerar mapa de calor: {str(e)}")

# Mapa das Macrorregiões
st.markdown("---")
st.subheader("Mapa das Macrorregiões")
try:
    fig_mapa = criar_mapa_macrorregioes(df_filtrado, indicador_selecionado)
    st.plotly_chart(fig_mapa, use_container_width=True)
except Exception as e:
    st.error(f"Erro ao gerar mapa das macrorregiões: {str(e)}")

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
