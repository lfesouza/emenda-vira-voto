-- Databricks notebook source
-- MAGIC %md
-- MAGIC # 03 — Gold
-- MAGIC - `senador_regras`: cobertura, municípios com emenda e entrada no ranking (regras do `PRD.md`, seção 7).
-- MAGIC - `emenda_mun_senador`: X por senador × município da UF, nos 3 cenários; município sem emenda = 0.
-- MAGIC - `voto_mun_senador`: Y = % dos votos válidos para Senador no município.
-- MAGIC - `correlacao_senador`: Spearman (ρ) por senador e cenário, com n.
-- MAGIC
-- MAGIC Cenários: `principal` (individuais 2020–2026, pagos até 09/2026), `transf_especiais` (só Transferências Especiais),
-- MAGIC `pagos_2026` (só pagamentos de 01 a 09/2026).

-- COMMAND ----------

CREATE OR REPLACE TABLE data_glow_up.gold.senador_regras AS
WITH em AS (
  SELECT
    id_senador,
    SUM(valor) AS rs_individual,
    SUM(CASE WHEN ente_municipal AND uf_favorecido = uf_senador THEN valor ELSE 0 END) AS rs_municipal_uf,
    COUNT(DISTINCT CASE WHEN ente_municipal AND uf_favorecido = uf_senador THEN id_municipio END) AS n_municipios_com_emenda
  FROM data_glow_up.silver.emenda_senador
  GROUP BY id_senador
)
SELECT
  s.*,
  coalesce(em.rs_individual, 0) AS rs_individual,
  coalesce(em.rs_municipal_uf, 0) AS rs_municipal_uf,
  ROUND(em.rs_municipal_uf / em.rs_individual * 100, 1) AS cobertura_pct,
  coalesce(em.n_municipios_com_emenda, 0) AS n_municipios_com_emenda,
  (SELECT COUNT(*) FROM data_glow_up.silver.populacao p WHERE p.sigla_uf = s.sigla_uf) AS n_municipios_uf,
  -- Regras de entrada: fora o DF, mínimo de 15 municípios com emenda, cobertura de 20%+
  s.sigla_uf <> 'DF'
    AND coalesce(em.n_municipios_com_emenda, 0) >= 15
    AND coalesce(em.rs_municipal_uf / em.rs_individual, 0) >= 0.2 AS no_ranking
FROM data_glow_up.silver.senador s
LEFT JOIN em USING (id_senador);

-- COMMAND ----------

CREATE OR REPLACE TABLE data_glow_up.gold.emenda_mun_senador AS
WITH em AS (
  SELECT
    id_senador,
    id_municipio,
    SUM(valor) AS rs_principal,
    SUM(CASE WHEN tipo_emenda = 'Emenda Individual - Transferências Especiais' THEN valor ELSE 0 END) AS rs_transf_especiais,
    SUM(CASE WHEN ano_mes >= '202601' THEN valor ELSE 0 END) AS rs_pagos_2026
  FROM data_glow_up.silver.emenda_senador
  WHERE ente_municipal AND uf_favorecido = uf_senador
  GROUP BY ALL
),
todos AS (
  SELECT id_municipio, SUM(valor) AS rs_todos
  FROM data_glow_up.silver.emenda_municipal_todos
  GROUP BY id_municipio
)
-- Todos os municípios da UF do senador; quem não recebeu emenda entra com 0
SELECT
  s.id_senador,
  s.sigla_uf,
  p.id_municipio,
  p.populacao,
  coalesce(em.rs_principal, 0) AS rs_principal,
  coalesce(em.rs_transf_especiais, 0) AS rs_transf_especiais,
  coalesce(em.rs_pagos_2026, 0) AS rs_pagos_2026,
  coalesce(em.rs_principal, 0) / p.populacao AS pc_principal,
  coalesce(em.rs_transf_especiais, 0) / p.populacao AS pc_transf_especiais,
  coalesce(em.rs_pagos_2026, 0) / p.populacao AS pc_pagos_2026,
  -- Placebo: emendas de todos os outros autores (deputados e demais senadores) para o mesmo município
  coalesce(t.rs_todos, 0) - coalesce(em.rs_principal, 0) AS rs_outros,
  (coalesce(t.rs_todos, 0) - coalesce(em.rs_principal, 0)) / p.populacao AS pc_outros
FROM data_glow_up.silver.senador s
JOIN data_glow_up.silver.populacao p ON p.sigla_uf = s.sigla_uf
LEFT JOIN em ON em.id_senador = s.id_senador AND em.id_municipio = p.id_municipio
LEFT JOIN todos t ON t.id_municipio = p.id_municipio;

-- COMMAND ----------

CREATE OR REPLACE TABLE data_glow_up.gold.voto_mun_senador AS
WITH total AS (
  SELECT id_municipio, SUM(votos_validos) AS votos_validos_senador
  FROM data_glow_up.silver.voto_municipio
  GROUP BY id_municipio
)
SELECT
  s.id_senador,
  v.id_municipio,
  v.votos_validos AS votos_senador,
  t.votos_validos_senador,
  v.votos_validos / t.votos_validos_senador * 100 AS pct_votos
FROM data_glow_up.silver.senador s
JOIN data_glow_up.silver.voto_municipio v ON v.sq_candidato = s.sq_candidato
JOIN total t USING (id_municipio);

-- COMMAND ----------

-- Spearman = correlação de Pearson entre os postos; empates recebem o posto médio
CREATE OR REPLACE TABLE data_glow_up.gold.correlacao_senador AS
WITH base AS (
  SELECT e.id_senador, c.cenario, c.x, v.pct_votos AS y
  FROM data_glow_up.gold.emenda_mun_senador e
  JOIN data_glow_up.gold.voto_mun_senador v USING (id_senador, id_municipio)
  LATERAL VIEW stack(3,
    'principal', e.pc_principal,
    'transf_especiais', e.pc_transf_especiais,
    'pagos_2026', e.pc_pagos_2026
  ) c AS cenario, x
),
postos AS (
  SELECT
    id_senador, cenario, x, y,
    RANK() OVER (PARTITION BY id_senador, cenario ORDER BY x)
      + (COUNT(*) OVER (PARTITION BY id_senador, cenario, x) - 1) / 2 AS posto_x,
    RANK() OVER (PARTITION BY id_senador, cenario ORDER BY y)
      + (COUNT(*) OVER (PARTITION BY id_senador, cenario, y) - 1) / 2 AS posto_y
  FROM base
)
SELECT
  r.id_senador, r.sigla_uf, r.nome_parlamentar, r.sigla_partido, r.situacao_2026, r.no_ranking,
  p.cenario,
  COUNT(*) AS n,
  SUM(CASE WHEN p.x > 0 THEN 1 ELSE 0 END) AS n_com_emenda,
  ROUND(corr(p.posto_x, p.posto_y), 4) AS rho
FROM postos p
JOIN data_glow_up.gold.senador_regras r USING (id_senador)
GROUP BY ALL;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Conferências

-- COMMAND ----------

-- Regras: esperado 29 no ranking, R$ 8,74 bi individuais e R$ 4,64 bi municipais na UF
SELECT COUNT(*) AS senadores, SUM(CASE WHEN no_ranking THEN 1 ELSE 0 END) AS no_ranking,
  ROUND(SUM(rs_individual) / 1e9, 2) AS rs_individual_bi, ROUND(SUM(rs_municipal_uf) / 1e9, 2) AS rs_municipal_uf_bi
FROM data_glow_up.gold.senador_regras;

-- X: soma do cenário principal = R$ municipal na UF; linhas = soma dos municípios das UFs dos 32
SELECT COUNT(*) AS linhas, ROUND(SUM(rs_principal) / 1e9, 2) AS rs_principal_bi,
  ROUND(SUM(rs_transf_especiais) / 1e9, 2) AS rs_te_bi, ROUND(SUM(rs_pagos_2026) / 1e9, 2) AS rs_2026_bi,
  SUM(CASE WHEN rs_outros < 0 THEN 1 ELSE 0 END) AS outros_negativo
FROM data_glow_up.gold.emenda_mun_senador;

-- Y: todo senador × município da UF precisa ter voto (esperado 0 faltando)
SELECT COUNT(*) AS sem_voto
FROM data_glow_up.gold.emenda_mun_senador e
LEFT ANTI JOIN data_glow_up.gold.voto_mun_senador v USING (id_senador, id_municipio);

-- Correlação, cenário principal
SELECT sigla_uf, nome_parlamentar, situacao_2026, no_ranking, n, n_com_emenda, rho
FROM data_glow_up.gold.correlacao_senador
WHERE cenario = 'principal'
ORDER BY no_ranking DESC, rho DESC;
