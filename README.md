# Emenda vira voto?

> Nos municípios que mais receberam emendas de um senador, ele teve mais votos em 2026?

Para cada um dos 32 senadores que tentaram a reeleição em 2026, comparamos, município a município e dentro do próprio estado, as emendas individuais pagas ao município (por habitante) com o percentual de votos que ele teve ali.
Em 18 dos 29 senadores analisados, a relação é positiva e estatisticamente significativa; o ρ de Spearman mediano é 0,24 e se mantém controlando pelo tamanho do município.
No teste placebo, com as emendas dos outros parlamentares, o ρ mediano cai para 0,08. Correlação não é causalidade.

- **Página (mapa de cada senador, gráficos e tabela):** https://lfesouza.github.io/emenda-vira-voto/
- **Metodologia, filtros e limitações:** [`METODOLOGIA.md`](METODOLOGIA.md) · escopo: [`PRD.md`](PRD.md) · tabelas e colunas: [`docs/fontes.md`](docs/fontes.md)
- **De onde vem cada número:** consultas em [`sql/gold/`](sql/gold/)

Análise para o desafio **#DataGlowUp** (dados do Senado). Emendas de 2020 a 2026, pagamentos até setembro de 2026, 1º turno de 04/10/2026.

## Fontes
- Emendas Parlamentares, Senado (legislativo e administrativo), diretório de municípios e população — [Base dos Dados](https://basedosdados.org)
- Emendas por favorecido (município de destino) — [Portal da Transparência (CGU)](https://portaldatransparencia.gov.br/download-de-dados/emendas-parlamentares)
- Resultados eleitorais e candidaturas 2026 — [Portal de Dados Abertos do TSE](https://dadosabertos.tse.jus.br)
- Malha municipal — [IBGE](https://servicodados.ibge.gov.br/api/docs/malhas)

## Stack
Python + `basedosdados` (BigQuery) · Databricks Free Edition (catálogo `data_glow_up`, bronze/silver/gold) · página estática com D3 no GitHub Pages · n8n em Docker (automação).

## Como reproduzir

**Pré-requisitos:** Python 3.12+; conta Google Cloud com um projeto para cobrança do BigQuery (a Base dos Dados é gratuita, a consulta usa a cota do seu projeto); workspace Databricks (a Free Edition basta) com a [CLI](https://docs.databricks.com/dev-tools/cli/) logada (`databricks auth login`) e um SQL warehouse.

1. **Ambiente**
   ```bash
   python -m venv .venv
   .venv/Scripts/python -m pip install basedosdados pandas pyarrow scipy   # Linux/macOS: .venv/bin/python
   ```
   Crie um `.env` na raiz (nunca versionado):
   ```
   GCP_BILLING_PROJECT=<seu-projeto-gcp>
   DATABRICKS_WAREHOUSE_ID=<id-do-seu-sql-warehouse>
   ```

2. **Dados brutos** (em `data/`, fora do git; endereços e datas de checagem em [`docs/fontes.md`](docs/fontes.md))
   - `data/tse/votacao_candidato_munzona_2026.zip` — https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_2026.zip
   - `data/tse_cand/consulta_cand_2026.zip` — https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_2026.zip
   - `data/portal/EmendasParlamentares.zip` — https://portaldatransparencia.gov.br/download-de-dados/emendas-parlamentares/UNICO
   - `data/tse2018/votacao_candidato_munzona_2018.zip` e `data/tse2018/consulta_cand_2018.zip` — mesmos endereços do TSE, trocando 2026 por 2018

3. **Universo e bronze** (na raiz do repositório)
   ```bash
   .venv/Scripts/python ingest/senadores_reeleicao.py data/tse_cand/consulta_cand_2026.zip data/portal/EmendasParlamentares.zip
   .venv/Scripts/python ingest/bronze.py
   .venv/Scripts/python ingest/bronze_2018.py   # eleição de 2018 (casamento pelo CPF)
   ```

4. **Databricks:** rode o primeiro bloco de `notebooks/01_bronze.sql` (cria catálogo, schemas e Volume), envie os arquivos e rode os notebooks em ordem
   ```bash
   databricks fs cp -r data/bronze dbfs:/Volumes/data_glow_up/bronze/arquivos --overwrite
   ```
   `01_bronze.sql` → `02_silver.sql` → `03_gold.sql` (SQL warehouse) → `04_correlacao.py` → `05_eleicao_2018.py` (computação serverless). Cada notebook termina com conferências (contagens e somas esperadas nos comentários).

5. **Números e página**
   ```bash
   .venv/Scripts/python ingest/exporta_site.py        # roda sql/gold/*.sql e grava site/data/
   .venv/Scripts/python -m http.server 8000 -d site   # abra http://localhost:8000
   ```

6. **Automação "Radar do Senado"** (opcional; PRD seção 9): boletim semanal com as votações nominais do Plenário e as despesas da cota parlamentar (CEAPS) acima da referência estatística do próprio histórico, enviado ao Telegram com um link para aprovar ou descartar num formulário do n8n. Texto por modelo fixo, sem LLM. Instruções em [`n8n/docker-compose.yml`](n8n/docker-compose.yml); workflow em [`n8n/radar_senado.json`](n8n/radar_senado.json).

O carrossel do LinkedIn fica em [`assets/carrossel/`](assets/carrossel/) (`carrossel.html` lê os mesmos dados da página).

Os arquivos de origem podem ser republicados (o TSE e o Portal atualizam os dados); números diferentes dos publicados aqui em 24/10/2026 podem vir dessa atualização.
