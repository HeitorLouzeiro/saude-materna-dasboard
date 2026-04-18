# Dashboard de Vigilancia de Saude Materna

Dashboard interativo para analise de indicadores de saude materna, com foco em
filtros temporais e regionais, visualizacoes estatisticas e mapa geografico com
camadas por ano.

## Visao Geral

Este projeto usa Streamlit para disponibilizar um painel de vigilancia com:

- Filtro por intervalo de anos
- Filtro por macro-regiao e regional
- Selecao de indicador de saude materna
- Estatisticas descritivas (media, mediana e desvio padrao)
- Graficos de distribuicao, serie temporal, heatmap e histograma
- Mapa interativo Folium por municipio, com controle de camadas por ano

Fonte de dados no app: Fiocruz.

## Principais Funcionalidades

- Filtros na barra lateral:
	- Periodo (ano inicial e final)
	- Macro-regiao
	- Regional
	- Indicador
	- Layout comparativo (automatico, lado a lado ou empilhado)
	- Altura do mapa
- Visualizacoes:
	- Estatisticas descritivas
	- Distribuicao por macro-regiao (barras)
	- Mapa de calor por regional x ano
	- Mapa interativo por municipio (Folium)
	- Linha do tempo do indicador
	- Distribuicao regional (pizza)
	- Histograma do indicador

## Tecnologias

- Python
- Streamlit
- Pandas
- Plotly
- Matplotlib
- Seaborn
- Folium + Branca
- GeoPandas (dependencia do ambiente)

As dependencias completas estao em `requirements.txt`.

## Estrutura do Projeto

```text
.
|- app.py
|- requirements.txt
|- data/
|  |- IndicadoresConsolidados_SaudeMaterna_empilhado.xlsx
|  |- geojs-22-mun.json
|- src/
	 |- config.py
	 |- data/
	 |  |- loader.py
	 |- visualizations/
	 |  |- charts.py
	 |  |- maps.py
	 |- utils/
			|- map_utils.py
```

## Pre-requisitos

- Python 3.10+ (recomendado)
- pip atualizado

No Windows, se necessario, habilite execucao de script apenas para a sessao do
terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

## Instalacao

1. Clone o repositorio:

```bash
git clone https://github.com/HeitorLouzeiro/saude-materna-dasboard.git
cd saude-materna-dasboard
```

2. Crie e ative um ambiente virtual:

Windows (PowerShell):

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python -m venv venv
source venv/bin/activate
```

3. Instale as dependencias:

```bash
pip install -r requirements.txt
```

## Como Executar

Com o ambiente virtual ativo:

```bash
streamlit run app.py
```

O Streamlit exibira a URL local (geralmente `http://localhost:8501`).

## Dados Esperados

O app le por padrao:

- `data/IndicadoresConsolidados_SaudeMaterna_empilhado.xlsx`
- `data/geojs-22-mun.json`

Colunas esperadas no Excel (minimo para funcionamento atual):

- `ANO`
- `Macro`
- `Regional`
- `MUN`
- `IN1(6 CONSULTAS)`
- `IN2 (HIV/SÍFILIS)`
- `IN3 (NV 6 CON)`
- `IN4(PARTOS_CES)`
- `IN5Q1 (RMM)`

## Configuracao e Customizacao

As configuracoes principais estao em `src/config.py`:

- `INDICADORES`: mapeamento de colunas para nomes amigaveis
- `PLOT_CONFIG`: cores e configuracoes visuais
- `DATA_PATH` e `GEOJSON_PATH`: caminhos de dados

Para adicionar novo indicador:

1. Garanta que a coluna exista no arquivo Excel
2. Adicione a chave no dicionario `INDICADORES`

## Troubleshooting

- Erro ao carregar dados:
	- Verifique se os arquivos existem em `data/`
	- Confirme o nome correto das colunas no Excel
- Tela sem dados apos filtro:
	- Amplie o periodo
	- Troque macro/regional para `Todas`
- Problemas com ambiente Python:
	- Recrie o ambiente virtual
	- Reinstale dependencias com `pip install -r requirements.txt`

## Licenca

Este projeto esta licenciado sob Apache License 2.0.

Consulte o arquivo `LICENSE` para detalhes.