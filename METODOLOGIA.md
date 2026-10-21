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

Números a reproduzir por query em `sql/gold/` quando a gold existir.

**De-para de nomes (silver, 20/10/2026):** o município do favorecido casa com o diretório da Base dos Dados por UF + nome normalizado. Os 9 nomes que não casavam (R$ 0,18 bi, todos os autores) são municípios renomeados, ligados manualmente ao código IBGE em `notebooks/02_silver.sql` (`depara_municipio_nome`): Brasópolis → Brazópolis (MG), Eldorado dos Carajás → Eldorado do Carajás (PA), Seridó → São Vicente do Seridó (PB), Trajano de Morais → Trajano de Moraes (RJ), Augusto Severo → Campo Grande (RN), Januário Cicco → Boa Saúde (RN), Presidente Juscelino → Serra Caiada (RN), Santana do Livramento → Sant'Ana do Livramento (RS), Embu → Embu das Artes (SP). Depois do de-para, nenhuma linha de ente municipal ficou sem código (0 linhas, R$ 0). Contagem de municípios por código IBGE = contagem por nome para os 32 senadores: ranking inalterado (29).

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
- **Votos (Y)** = votos nominais válidos do senador no município ÷ votos nominais válidos de todos os candidatos a Senador no município (`QT_VOTOS_NOMINAIS_VALIDOS`, zonas somadas, 1º turno). Ficam fora do denominador os votos `Anulado` (25.284) e `Anulado sub judice` (364.824). Em 2026 cada eleitor votou em 2 senadores, então a soma dos percentuais de todos os candidatos de um município é 200%.
- **População:** estimativa IBGE de 2025 (`br_ibge_populacao.municipio`, ano mais recente disponível; 5.571 municípios, 213.421.037 habitantes). **Correção de fonte (20/10/2026):** em 2025 a tabela tem 1 linha sem `id_municipio` e sem `sigla_uf` (5.877 hab.), e Boa Esperança do Norte/MT (5101837), município novo, é o único do diretório sem população. A linha foi atribuída a ele no silver (5.804 votos válidos para Senador no município; R$ 349.989 em emendas de um dos 32). Nenhuma linha ou R$ descartado.
- **Robustez** (`notebooks/04_correlacao.py`, tabela `gold.robustez_senador`, cenário principal):
  - *Ponderado (sensibilidade do PRD):* correlação de Pearson ponderada pelos votos válidos para Senador do município, sobre os postos de X e Y. Votos válidos são proxy do eleitorado (decisão de 20/10/2026). Sem valor-p padrão; reportado só o ρ.
  - *Parcial:* Spearman entre X e Y controlando pela população — correlação parcial sobre os postos, valor-p pela t com n − 3 g.l. Testa se o ρ é só efeito do tamanho do município (per capita é maior em município pequeno).
  - *Placebo 1 — emenda dos outros:* X trocado pelas emendas individuais per capita de todos os outros autores (deputados e demais senadores) para o município, mesma janela e critério de ente municipal (`silver.emenda_municipal_todos`), contra o voto do senador. Se o placebo for tão alto quanto o ρ original, a relação reflete o perfil do município, não a emenda do senador.
  - *Placebo 2 — voto dos outros:* X do senador contra o % de cada outro candidato a Senador da UF (mediana dos ρ). Referência fraca: os percentuais de um município somam 200%, o que puxa o ρ para baixo mecanicamente.
- **Emenda per capita (X)** = soma do `Valor Recebido` das emendas individuais do senador cujo favorecido é o ente municipal do município (UF do senador, ano da emenda 2020–2026, pagamentos até 09/2026) ÷ população 2025. Cenários: `principal`; `transf_especiais` (só `Emenda Individual - Transferências Especiais`); `pagos_2026` (só `Ano/Mês` de 202601 a 202609). **Decisão (20/10/2026):** todos os municípios da UF do senador entram na correlação; quem não recebeu emenda do senador entra com X = 0. Assim, o n de cada senador é o número de municípios da UF. O mínimo de 15 municípios *com emenda* continua valendo como regra de entrada no ranking.

## Onde está cada número
Queries de reprodução em `sql/gold/` (rodam sobre o catálogo `data_glow_up`):
- `01_totais.sql`: 32 senadores, 14 eleitos, 29 no ranking; R$ 8,74 bi em emendas individuais, R$ 4,64 bi (53,1%) atribuíveis a municípios da própria UF, 46,9% sem município identificado.
- `02_resumo_cenarios.sql`: por cenário, quantos ρ positivos/negativos com p < 0,05 e ρ mediano.
- `03_robustez.sql`: medianas e contagens da parcial, ponderada e dos placebos.
- `04_ranking.sql`: tabela dos 32 com n, ρ, valor-p, testes e motivo de quem fica fora do ranking.

## Pipeline (Databricks, catálogo `data_glow_up`)
- **Bronze** (`notebooks/01_bronze.sql`): arquivos brutos em Parquet gerados por `ingest/bronze.py` e enviados ao Volume `bronze.arquivos`. Único filtro: a votação TSE entra só com o cargo Senador (74.447 das 6.730.564 linhas do arquivo). Tabelas: `emenda_favorecido` (827.457), `votacao_senador_munzona` (74.447), `municipio` (5.571), `populacao` (191.099), `senador_reeleicao` (32).
- **Silver** (`notebooks/02_silver.sql`): `senador` (32), `emenda_senador` (29.167 linhas; R$ 8,74 bi individuais, dos quais R$ 4,64 bi de ente municipal na UF), `voto_municipio` (votos válidos por candidato e município; 207.038.240 votos, 5.571 municípios, os 32 presentes), `populacao` (2025). O de-para código TSE → IBGE pelo diretório casa 100% dos municípios.

## Limitações
- **Distrito Federal fora da análise.** O DF tem um único "município" (Brasília), então a comparação município a município dentro do estado não se aplica.
- **Estados com poucos municípios.** Roraima tem 15 municípios e o Amapá, 16: o mínimo de 15 municípios fica no limite ou é inatingível. Chico Rodrigues (RR) fica fora com 14; os dois senadores do AP entram com n = 16, e a correlação deles deve ser lida com a cautela de amostra pequena.
- **Pagamentos via Banco do Brasil.** R$ 39,77 bi das emendas individuais 2019–2026 têm o Banco do Brasil como favorecido no arquivo do Portal da Transparência, sem identificação do município de destino. Esses valores ficam fora da atribuição municipal; limitação conhecida da fonte.
