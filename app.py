import matplotlib.pyplot as plt
import streamlit as st

# Título do dashboard
st.title("Dashboard de Vigilância de Saúde Materna")

# Filtros
st.sidebar.header("Filtros")

# Intervalo de Anos
ano_inicio, ano_fim = st.sidebar.slider(
    "Intervalo de anos", 2012, 2023, (2012, 2023))
st.sidebar.write(f"Anos selecionados: {ano_inicio} - {ano_fim}")

# Nível de Análise
nivel_analise = st.sidebar.selectbox("Nível de análise",
                                     ["Nacional", "Estadual", "Municipal"])
st.sidebar.write(f"Nível de análise: {nivel_analise}")

# Bloco de Indicadores
bloco_indicadores = st.sidebar.selectbox("Bloco de indicadores", [
    "1 - Condições socioeconômicas e de acesso ao serviço de saúde",
    "2 - Planejamento reprodutivo",
    "3 - Assistência pré-natal",
    "4 - Assistência ao parto",
    "5 - Condições de nascimento",
    "6 - Mortalidade e morbidade materna"
])
st.sidebar.write(f"Bloco de indicadores: {bloco_indicadores}")

# Indicador
indicador = st.sidebar.selectbox("Indicador", [
    "Porcentagem de nascidos vivos de mães com idade inferior a 20 anos",
    "Porcentagem de nascidos vivos de mães com idade entre 20 a 34 anos",
    "Porcentagem de nascidos vivos de mães com idade de 35 ou mais anos",
    "Porcentagem de nascidos vivos de mães de raça/cor branca",
    "Porcentagem de nascidos vivos de mães de raça/cor preta",
    "Porcentagem de nascidos vivos de mães de raça/cor parda",
    "Porcentagem de nascidos vivos de mães de raça/cor amarela",
    "Porcentagem de nascidos vivos de mães de raça/cor indígena",
    "Porcentagem de nascidos vivos de mães com menos de 4 anos de estudo",
    "Porcentagem de nascidos vivos de mães com 4 a 7 anos de estudo",
    "Porcentagem de nascidos vivos de mães com 8 a 11 anos de estudo",
    "Porcentagem de nascidos vivos de mães com mais de 11 anos de estudo",
    "Porcentagem de mulheres com 10 a 49 anos usuárias exclusivas do SUS",
    "Cobertura populacional com equipes de Saúde da Família"
])
st.sidebar.write(f"Indicador: {indicador}")

# Botão de Atualizar Resultados
if st.sidebar.button("Atualizar resultados"):
    st.sidebar.write(
        "Resultados atualizados com base nos filtros selecionados.")

# Gráfico de Resumo da Qualidade da Informação
st.subheader("Resumo da Qualidade da Informação")
qualidade = 75  # Exemplo de porcentagem
st.metric(label="Qualidade da Informação", value=f"{qualidade}%", delta="")

# Gráfico de Distribuição do Indicador por Região
st.subheader("Distribuição do Indicador por Região do País")
regioes = ['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul']
valores = [15, 25, 20, 30, 10]  # Exemplo de dados
plt.figure(figsize=(10, 6))
plt.bar(regioes, valores, color=['orange', 'pink', 'purple', 'blue', 'black'])
plt.title("Distribuição do Indicador")
plt.xlabel("Região")
plt.ylabel("Porcentagem")
st.pyplot(plt)
plt.close()

# Gráfico de Evolução do Indicador ao Longo do Período
st.subheader("Evolução do Indicador ao Longo do Período")
anos = [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]
evolucao = [20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9]  # Dados fictícios
plt.figure(figsize=(10, 6))
plt.plot(anos, evolucao, marker='o', color='purple')
plt.title("Evolução do Indicador")
plt.xlabel("Ano")
plt.ylabel("Porcentagem")
plt.grid(True)
st.pyplot(plt)
plt.close()

# Campos de entrada para dados do usuário
gestational_age = st.number_input(
    "Idade gestacional (semanas)", min_value=0, max_value=42)
birth_weight = st.number_input(
    "Peso ao nascer (kg)", min_value=0.0, max_value=10.0)

# Exibir os dados de entrada
st.write(f"Idade gestacional: {gestational_age} semanas")
st.write(f"Peso ao nascer: {birth_weight} kg")

# Placeholder para futuras visualizações
st.write("Visualizações virão aqui.")
