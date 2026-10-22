-- Casos concretos: para os 3 senadores do ranking com maior ρ (cenário principal), o município da UF com a maior
-- emenda per capita entre os com mais de 10 mil habitantes (IBGE 2025), com R$/hab. e % dos votos válidos 2026.
-- rho_placebo_emenda_outros: ρ do voto do senador com a emenda per capita dos outros parlamentares (03_robustez).
WITH top3 AS (
  SELECT r.id_senador, r.rho, r.p_valor, r.rho_placebo_emenda_outros, s.n_municipios_uf AS n
  FROM data_glow_up.gold.robustez_senador r
  JOIN data_glow_up.gold.senador_regras s USING (id_senador)
  WHERE s.no_ranking
  ORDER BY r.rho DESC
  LIMIT 3
),
mun AS (
  SELECT
    e.id_senador, m.nome AS municipio, e.populacao, e.rs_principal, e.pc_principal, v.pct_votos,
    ROW_NUMBER() OVER (PARTITION BY e.id_senador ORDER BY e.pc_principal DESC) AS ordem
  FROM data_glow_up.gold.emenda_mun_senador e
  JOIN data_glow_up.gold.voto_mun_senador v USING (id_senador, id_municipio)
  JOIN data_glow_up.bronze.municipio m USING (id_municipio)
  WHERE e.populacao > 10000
)
SELECT
  s.sigla_uf,
  s.nome_parlamentar,
  t.n,
  ROUND(t.rho, 3) AS rho,
  ROUND(t.p_valor, 4) AS p_valor,
  ROUND(t.rho_placebo_emenda_outros, 3) AS rho_placebo_emenda_outros,
  mun.municipio,
  mun.populacao,
  ROUND(mun.rs_principal / 1e6, 2) AS rs_mi,
  ROUND(mun.pc_principal, 2) AS rs_por_habitante,
  ROUND(mun.pct_votos, 2) AS pct_votos_2026
FROM top3 t
JOIN data_glow_up.gold.senador_regras s USING (id_senador)
JOIN mun ON mun.id_senador = t.id_senador AND mun.ordem = 1
ORDER BY t.rho DESC;
