# Metodologia

Documento vivo. Regras de cálculo definidas no `PRD.md`, seção 7.

## Fontes
Ver [`docs/fontes.md`](docs/fontes.md).

## Filtros e descartes
Cada filtro registra: linhas removidas, R$ removidos e motivo.

| Etapa | Filtro | Linhas removidas | R$ removidos | Motivo |
|---|---|---|---|---|

### Observações do perfil exploratório (19/10/2026)
Emendas individuais 2019–2025 na tabela `br_cgu_emendas_parlamentares.microdados`: R$ 101,75 bi pagos; apenas R$ 10,34 bi (~10%) com município identificado. A base não traz 2026. Detalhes em `docs/fontes.md` (F1).

### Atribuição de município pelo favorecido (provisório, 20/10/2026)
Fonte: `EmendasParlamentares_PorFavorecido.csv` (F1b). Critério: a emenda conta para o município **somente quando o favorecido é o próprio ente municipal** — `Natureza Jurídica` em `Município`, `Fundo Público da Administração Direta Municipal` ou `Órgão Público do Poder Executivo Municipal`. Demais favorecidos ficam fora.

Emendas individuais, ano da emenda 2019–2026, R$ = `Valor Recebido`:

| Recorte | Total | Atribuível a município | Excluído |
|---|---|---|---|
| Individuais 2019–2026 | R$ 116,77 bi (314.198 linhas) | R$ 59,48 bi — 50,9% (121.000 linhas) | R$ 57,29 bi — 49,1% (193.198 linhas) |
| Individuais 2019–2025 | R$ 100,95 bi | R$ 45,25 bi — 44,8% | R$ 55,70 bi — 55,2% |
| Transferências Especiais 2019–2026 | R$ 32,15 bi | R$ 29,72 bi — 92,4% | R$ 2,43 bi — 7,6% |
| Finalidade Definida 2019–2026 | R$ 84,62 bi | R$ 29,76 bi — 35,2% | R$ 54,86 bi — 64,8% |

Principais exclusões (individuais 2019–2026): Banco do Brasil como favorecido R$ 39,77 bi; Associação Privada R$ 5,98 bi; Sociedade Empresária Limitada R$ 3,58 bi; Estado ou DF + fundos/órgãos estaduais R$ 5,00 bi; Fundação Privada R$ 1,79 bi. Autarquias e fundações municipais (R$ 0,03 bi) também ficam fora pelo critério.

Pagamentos posteriores à eleição (`Ano/Mês` = 202610): R$ 0,04 bi. Cortando em 202609: individuais R$ 116,72 bi, atribuível R$ 59,47 bi (51,0%), excluído R$ 57,25 bi; Transferências Especiais inalteradas (92,4%).

Os números acima são do perfil inicial (janela 2019–2026, todos os autores). A janela final é 2020–2026 (ver Regras do ranking).

**Decisão (20/10/2026):**
- **Análise principal:** emendas individuais (ano da emenda 2020–2026), critério de ente municipal, pagamentos até `Ano/Mês` = 202609.
- **Sensibilidade (a):** só `Emenda Individual - Transferências Especiais`.
- **Sensibilidade (b):** só pagamentos realizados em 2026 (`Ano/Mês` de 202601 a 202609).

Pendências: de-para manual dos 9 nomes de município que não casam (R$ 0,18 bi). Números a reproduzir por query em `sql/gold/` quando a gold existir.

### Universo: 32 senadores (20/10/2026, `ingest/senadores_reeleicao.py`)
- Partida: 54 senadores em exercício com `mandato` = `2019 / 2027` em `br_senado_dados_abertos_administrativos.senador` (47 titulares, 7 suplentes).
- Cruzamento com candidaturas a Senador 2026 (`consulta_cand_2026_BRASIL.csv`, TSE) por UF + nome completo normalizado (sem acento, maiúsculas): **32 casados, 14 `ELEITO` e 18 `NÃO ELEITO`** — confere com o PRD. Conferência: os 21 candidatos com ocupação declarada "senador" estão todos entre os 32.
- Autor da emenda → senador: `Nome do Autor da Emenda` (Portal) = `nome_parlamentar` (Senado), normalizados. Na janela 2020–2026, cada um dos 32 casa com exatamente 1 código de autor. (Na janela 2019–2026, 5 senadores — Eliziane Gama, Esperidião Amin, Marcelo Castro, Veneziano Vital do Rêgo, Zenaide Maia — tinham um segundo código usado só em emendas de 2019, apresentadas no fim de 2018 quando eram deputados federais.)

### Regras do ranking (decididas em 20/10/2026)
1. **Janela de ano da emenda 2020–2026 para todos:** só emendas apresentadas durante o mandato 2019–2027. As emendas de ano 2019 foram apresentadas no fim de 2018, no mandato anterior (de deputado ou de senador). Efeito nos 32: R$ 8,90 bi → R$ 8,74 bi em emendas individuais; R$ 4,69 bi → R$ 4,64 bi atribuíveis a municípios. Mudaram 11 senadores: os 5 ex-deputados acima e 6 que já eram senadores antes de 2019 (Sérgio Petecão, Renan Calheiros, Eduardo Braga, Randolfe Rodrigues, Humberto Costa, Ciro Nogueira).
2. **Cobertura mínima de 20%:** o R$ atribuível a municípios da própria UF precisa ser pelo menos 20% do R$ em emendas individuais do senador. Sai: Jaques Wagner (BA) — 26 municípios, mas R$ 0,1 mi de R$ 280,7 mi (0,0%); suas emendas tiveram como favorecidos o governo estadual (Estado da Bahia e Fundo Estadual de Saúde, R$ 136 mi) e o Banco do Brasil (R$ 81 mi). Na página, aparece como perfil de destinação ao governo estadual.
3. **Mínimo de 15 municípios distintos** com emenda (mantido do PRD). Sai: Chico Rodrigues (RR, 14 municípios).

Resultado (análise principal, janela 2020–2026): 32 senadores; 30 com 15+ municípios; 30 com cobertura 20%+; **29 no ranking**. Fora: Leila Barros (DF), Jaques Wagner (cobertura), Chico Rodrigues (mínimo de municípios). Nenhum R$ municipal fora da UF do senador. Tabela completa: `data/senadores_reeleicao.csv` (gerada pelo script).

## Fórmulas
_(a preencher)_

## Limitações
- **Distrito Federal fora da análise.** O DF tem um único "município" (Brasília), então a comparação município a município dentro do estado não se aplica.
- **Estados com poucos municípios.** Roraima tem 15 municípios e o Amapá, 16: o mínimo de 15 municípios fica no limite ou é inatingível. Chico Rodrigues (RR) fica fora com 14; os dois senadores do AP entram com n = 16, e a correlação deles deve ser lida com a cautela de amostra pequena.
- **Pagamentos via Banco do Brasil.** R$ 39,77 bi das emendas individuais 2019–2026 têm o Banco do Brasil como favorecido no arquivo do Portal da Transparência, sem identificação do município de destino. Esses valores ficam fora da atribuição municipal; limitação conhecida da fonte.
