# Emenda vira voto?

> Nos municípios que mais receberam emendas de um senador, ele teve mais votos em 2026?

Análise para o desafio **#DataGlowUp** (dados do Senado): emendas parlamentares individuais (2019–2026) × votação de 2026, município a município, dentro do estado, para os 32 senadores que tentaram a reeleição.

**Página:** https://lfesouza.github.io/emenda-vira-voto/ · **Status:** em construção — publicação prevista para 24/10/2026.

Correlação não é causalidade. Fontes, filtros e limitações em [`METODOLOGIA.md`](METODOLOGIA.md); escopo completo em [`PRD.md`](PRD.md).

## Fontes
- Emendas Parlamentares (CGU/Portal da Transparência), Senado legislativo e administrativo — [Base dos Dados](https://basedosdados.org)
- Resultados eleitorais 2026 — [Portal de Dados Abertos do TSE](https://dadosabertos.tse.jus.br)
- População municipal — IBGE

Detalhe de tabelas e colunas em [`docs/fontes.md`](docs/fontes.md).

## Stack
Python + `basedosdados` (BigQuery) · Databricks Free Edition (bronze/silver/gold) · página estática no GitHub Pages · n8n em Docker.

## Como reproduzir
Em construção. Será necessária uma conta Google Cloud própria (projeto de cobrança para o BigQuery).
