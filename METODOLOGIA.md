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

**Decisão (20/10/2026):**
- **Análise principal:** emendas individuais (ano da emenda 2019–2026), critério de ente municipal, pagamentos até `Ano/Mês` = 202609.
- **Sensibilidade (a):** só `Emenda Individual - Transferências Especiais`.
- **Sensibilidade (b):** só pagamentos realizados em 2026 (`Ano/Mês` de 202601 a 202609).

Pendências: de-para manual dos 9 nomes de município que não casam (R$ 0,18 bi). Números a reproduzir por query em `sql/gold/` quando a gold existir.

## Fórmulas
_(a preencher)_

## Limitações
- **Distrito Federal fora da análise.** O DF tem um único "município" (Brasília), então a comparação município a município dentro do estado não se aplica.
- **Pagamentos via Banco do Brasil.** R$ 39,77 bi das emendas individuais 2019–2026 têm o Banco do Brasil como favorecido no arquivo do Portal da Transparência, sem identificação do município de destino. Esses valores ficam fora da atribuição municipal; limitação conhecida da fonte.
