# Fontes de dados

Nomes de tabelas e colunas copiados de consultas reais (nunca digitados de memória). Cada seção traz a data da consulta.

## F4 — TSE: votação por candidato e município (2026)

- **Arquivo:** `votacao_candidato_munzona_2026.zip`
- **URL:** https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_2026.zip
- **Checagem em 19/10/2026:** HTTP 200, 455.353.845 bytes, `Last-Modified: Mon, 19 Oct 2026 20:16:42 GMT`
- **Geração (coluna `DT_GERACAO`/`HH_GERACAO`):** 19/10/2026 16:31:51 — o TSE pode republicar; conferir a data antes da análise final.
- **Conteúdo do zip:** 29 CSVs (`_BRASIL`, `_BR` e um por UF) + `leiame.pdf`. CSV separado por `;`, encoding latin-1.
- **Granularidade:** candidato × município × zona eleitoral. Apenas 1º turno (`NR_TURNO` = 1), eleição de 04/10/2026.
- **Go/no-go (19/10/2026):** **GO.** `votacao_candidato_munzona_2026_BRASIL.csv` tem 6.730.564 linhas, das quais 74.447 com `DS_CARGO` = `Senador`, cobrindo as 27 UFs. Situação para Senador: 12.212 linhas `ELEITO`, 62.235 `NÃO ELEITO`.
- **Atenção:** `CD_MUNICIPIO` é o código do TSE, não o do IBGE → exige de-para (F6).
- **Colunas** (ordem do arquivo):

| Coluna | Uso previsto |
|---|---|
| `DT_GERACAO`, `HH_GERACAO` | versão do arquivo |
| `ANO_ELEICAO`, `CD_TIPO_ELEICAO`, `NM_TIPO_ELEICAO`, `NR_TURNO`, `CD_ELEICAO`, `DS_ELEICAO`, `DT_ELEICAO`, `TP_ABRANGENCIA` | filtro da eleição |
| `SG_UF`, `SG_UE`, `NM_UE` | UF |
| `CD_MUNICIPIO`, `NM_MUNICIPIO` | município (código TSE) |
| `NR_ZONA` | zona (somar por município) |
| `CD_CARGO`, `DS_CARGO` | filtro `Senador` (`CD_CARGO` = 5) |
| `SQ_CANDIDATO`, `NR_CANDIDATO`, `NM_CANDIDATO`, `NM_URNA_CANDIDATO`, `NM_SOCIAL_CANDIDATO` | candidato |
| `CD_SITUACAO_CANDIDATURA`, `DS_SITUACAO_CANDIDATURA`, `CD_DETALHE_SITUACAO_CAND`, `DS_DETALHE_SITUACAO_CAND`, `CD_SITUACAO_JULGAMENTO`, `DS_SITUACAO_JULGAMENTO`, `CD_SITUACAO_CASSACAO`, `DS_SITUACAO_CASSACAO`, `CD_SITUACAO_DCONST_DIPLOMA`, `DS_SITUACAO_DCONST_DIPLOMA` | situação da candidatura |
| `TP_AGREMIACAO`, `NR_PARTIDO`, `SG_PARTIDO`, `NM_PARTIDO`, `NR_FEDERACAO`, `NM_FEDERACAO`, `SG_FEDERACAO`, `DS_COMPOSICAO_FEDERACAO`, `SQ_COLIGACAO`, `NM_COLIGACAO`, `DS_COMPOSICAO_COLIGACAO` | partido |
| `ST_VOTO_EM_TRANSITO` | voto em trânsito |
| `QT_VOTOS_NOMINAIS`, `NM_TIPO_DESTINACAO_VOTOS`, `QT_VOTOS_NOMINAIS_VALIDOS` | **Y** (votos) |
| `CD_SIT_TOT_TURNO`, `DS_SIT_TOT_TURNO` | eleito / não eleito |

## Base dos Dados — como os nomes foram obtidos (19/10/2026)

- IDs do BigQuery: API do catálogo (`https://backend.basedosdados.org/graphql`, campo `cloudTables`).
- Colunas: `basedosdados.<dataset>.INFORMATION_SCHEMA.COLUMNS`, via `ingest/lista_schemas.py <dataset>`.
- Observação: `basedosdados.region-us.INFORMATION_SCHEMA.SCHEMATA` (lista de datasets do projeto) retorna 403 — o acesso público é por dataset.

## F1 — Emendas Parlamentares (CGU/Portal da Transparência)

**Tabela:** `basedosdados.br_cgu_emendas_parlamentares.microdados`

| # | Coluna | Tipo |
|---|---|---|
| 1 | `ano_emenda` | INT64 |
| 2 | `id_emenda` | STRING |
| 3 | `numero_emenda` | STRING |
| 4 | `tipo_emenda` | STRING |
| 5 | `id_autor_emenda` | STRING |
| 6 | `nome_autor_emenda` | STRING |
| 7 | `localidade` | STRING |
| 8 | `sigla_uf_gasto` | STRING |
| 9 | `id_municipio_gasto` | STRING |
| 10 | `id_funcao` | STRING |
| 11 | `nome_funcao` | STRING |
| 12 | `id_subfuncao` | STRING |
| 13 | `nome_subfuncao` | STRING |
| 14 | `id_programa` | STRING |
| 15 | `nome_programa` | STRING |
| 16 | `id_acao` | STRING |
| 17 | `nome_acao` | STRING |
| 18 | `id_plano_orcamentario` | STRING |
| 19 | `nome_plano_orcamentario` | STRING |
| 20 | `valor_empenhado` | FLOAT64 |
| 21 | `valor_liquidado` | FLOAT64 |
| 22 | `valor_pago` | FLOAT64 |
| 23 | `valor_resto_pagar_inscrito` | FLOAT64 |
| 24 | `valor_resto_pagar_cancelado` | FLOAT64 |
| 25 | `valor_resto_pagar_pagos` | FLOAT64 |

**Pontos de atenção:**
- O autor só é identificado por `id_autor_emenda`/`nome_autor_emenda` (código do Portal da Transparência), **sem ID do Senado nem do TSE** → casar com os 32 senadores por nome (registrar regra e casos ambíguos na METODOLOGIA).
- Valor pago (PRD): `valor_pago` + `valor_resto_pagar_pagos`.
- **Perfil (19/10/2026, `ingest/perfil_emendas.py`):**
  - Cobertura: `ano_emenda` de **2014 a 2025** (88.993 linhas). **Não há 2026.**
  - `tipo_emenda` (2019–2025, R$ pago = `valor_pago` + `valor_resto_pagar_pagos`): `Emenda Individual - Transferências com Finalidade Definida` (41.442 linhas, R$ 74,08 bi), `Emenda Individual - Transferências Especiais` (4.430; R$ 27,66 bi), `Emenda de Bancada` (2.369; R$ 43,31 bi), `Emenda de Relator` (547; R$ 40,47 bi), `Emenda de Comissão` (422; R$ 21,59 bi).
  - `id_municipio_gasto` nunca é nulo: quando não há município vem o texto `Sem informação`.
  - **Individuais 2019–2025 com município válido (casa com o diretório): 12.344 linhas, R$ 10,34 bi de R$ 101,75 bi (~10%).** Sem município: 33.528 linhas, R$ 91,40 bi — dos quais R$ 89,34 bi com `localidade` nula e R$ 2,07 bi com `localidade` = Nacional/regiões/Exterior.
- Existe outro dataset "Emendas Parlamentares" (Congresso Nacional) no catálogo, sem tabela no BigQuery — não usado.

## F1b — Emendas por favorecido (Portal da Transparência, fonte externa complementar)

- **Download:** https://portaldatransparencia.gov.br/download-de-dados/emendas-parlamentares/UNICO → redireciona para `https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/emendas-parlamentares/EmendasParlamentares.zip`
- **Checagem:** HTTP 200, 32.490.844 bytes, `Last-Modified: Sat, 10 Oct 2026 02:57:21 GMT`.
- **Conteúdo do zip:** `EmendasParlamentares.csv` (mesma base da F1), `EmendasParlamentares_Convenios.csv`, **`EmendasParlamentares_PorFavorecido.csv`** (827.457 linhas; `Ano/Mês` de pagamento de 201406 a 202610). CSV `;`, latin-1, decimal com vírgula.
- **Colunas de `EmendasParlamentares_PorFavorecido.csv`:** `Código da Emenda`, `Código do Autor da Emenda`, `Nome do Autor da Emenda`, `Número da emenda`, `Tipo de Emenda`, `Ano/Mês`, `Código do Favorecido`, `Favorecido`, `Natureza Jurídica`, `Tipo Favorecido`, `UF Favorecido`, `Município Favorecido`, `Valor Recebido`.
- **Atenção:**
  - Município do favorecido vem **só por nome** (sem código IBGE). Casamento por nome+UF normalizados (sem acento, maiúsculas) com `br_bd_diretorios_brasil.municipio`: 99,7% do R$ do critério municipal casa; 9 nomes não casam (ex.: `EMBU`/SP, `PRESIDENTE JUSCELINO`/RN, `SANTANA DO LIVRAMENTO`/RS) — de-para manual no silver.
  - Ano da emenda = 4 primeiros dígitos de `Código da Emenda` (mesmo critério de `ano_emenda` da F1).
  - R$ 39,77 bi das individuais 2019–2026 têm como favorecido o **BANCO DO BRASIL SA** (`00000000000191`, natureza Sociedade de Economia Mista) — intermediário, sem município de destino.
  - Os dados vão até `Ano/Mês` = 202610, ou seja, **incluem pagamentos posteriores à eleição de 04/10/2026**.
- **Perfil:** `ingest/perfil_favorecido.py data/portal/EmendasParlamentares.zip`.

## F2 — Senado legislativo

**Dataset:** `basedosdados.br_senado_dados_abertos` — 18 tabelas: `bloco`, `comissao`, `discurso`, `lideranca`, `mesa`, `partido`, `processo`, `relatoria`, `senador`, `senador_cargo`, `senador_comissao`, `senador_filiacao`, `senador_mandato`, `votacao`, `votacao_comissao`, `votacao_comissao_parlamentar`, `votacao_orientacao_bancada`, `votacao_parlamentar`.

Tabelas usadas na análise:

**`senador`:** `id_senador` STRING, `nome` STRING, `nome_completo` STRING, `sexo` STRING, `forma_tratamento` STRING, `sigla_partido` STRING, `sigla_uf` STRING, `email` STRING, `url_foto` STRING, `url_pagina` STRING, `url_pagina_particular` STRING, `id_publico_legislatura_atual` STRING

**`senador_mandato`:** `id_senador` STRING, `id_mandato` STRING, `sigla_uf` STRING, `participacao` STRING, `numero_legislatura_1` STRING, `data_inicio_legislatura_1` DATE, `data_fim_legislatura_1` DATE, `numero_legislatura_2` STRING, `data_inicio_legislatura_2` DATE, `data_fim_legislatura_2` DATE

**`senador_filiacao`:** `id_senador` STRING, `id_partido` STRING, `sigla_partido` STRING, `data_filiacao` DATE, `data_desfiliacao` DATE

## F3 — Senado administrativo

**Dataset:** `basedosdados.br_senado_dados_abertos_administrativos` — 40 tabelas (contratações, servidores, suprimento de fundos etc.). Usadas:

**`despesa_ceaps`:** `ano` INT64, `mes` INT64, `id_despesa` STRING, `id_senador` STRING, `tipo_despesa` STRING, `tipo_documento` STRING, `documento` STRING, `data` DATE, `cpf_cnpj_fornecedor` STRING, `nome_fornecedor` STRING, `detalhamento` STRING, `valor_reembolsado` FLOAT64

**`senador`:** `id_senador` STRING, `nome_parlamentar` STRING, `nome_completo` STRING, `sexo` STRING, `sigla_uf` STRING, `sigla_partido` STRING, `titular_suplente` STRING, `mandato` STRING, `data_nascimento` DATE, `email` STRING, `indicador_em_exercicio` STRING

## F5 — População municipal (IBGE)

**Tabela:** `basedosdados.br_ibge_populacao.municipio` — `ano` INT64, `sigla_uf` STRING, `id_municipio` STRING, `populacao` INT64. Ano mais recente disponível: a conferir na noite 2.

## F6 — Diretório de municípios

**Tabela:** `basedosdados.br_bd_diretorios_brasil.municipio` — 5.571 linhas (consulta de 19/10/2026).

Colunas: `id_municipio` STRING (IBGE 7 dígitos), `id_municipio_6` STRING, **`id_municipio_tse` STRING** (de-para com F4), `id_municipio_rf` STRING, `id_municipio_bcb` STRING, `nome` STRING, `capital_uf` INT64, `id_comarca` STRING, `id_regiao_saude` STRING, `nome_regiao_saude` STRING, `id_regiao_imediata` STRING, `nome_regiao_imediata` STRING, `id_regiao_intermediaria` STRING, `nome_regiao_intermediaria` STRING, `id_microrregiao` STRING, `nome_microrregiao` STRING, `id_mesorregiao` STRING, `nome_mesorregiao` STRING, `id_regiao_metropolitana` STRING, `nome_regiao_metropolitana` STRING, `ddd` STRING, `id_uf` STRING, `sigla_uf` STRING, `nome_uf` STRING, `nome_regiao` STRING, `amazonia_legal` INT64, `centroide` GEOGRAPHY
