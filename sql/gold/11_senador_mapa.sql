-- Senador do slide de mapa: maior ρ (cenário principal) entre os do ranking cujo placebo (emenda dos outros)
-- fica pelo menos 0,2 abaixo do próprio ρ. Traz o município do caso concreto dele (mesma regra de 09_casos_concretos:
-- maior emenda per capita entre os municípios com mais de 10 mil habitantes).
WITH escolhido AS (
  SELECT r.id_senador, r.rho, r.p_valor, r.rho_placebo_emenda_outros, s.n_municipios_uf AS n
  FROM data_glow_up.gold.robustez_senador r
  JOIN data_glow_up.gold.senador_regras s USING (id_senador)
  WHERE s.no_ranking AND r.rho - r.rho_placebo_emenda_outros >= 0.2
  ORDER BY r.rho DESC
  LIMIT 1
),
mun AS (
  SELECT
    e.id_senador, e.id_municipio, m.nome AS municipio, e.populacao, e.pc_principal, v.pct_votos,
    ROW_NUMBER() OVER (PARTITION BY e.id_senador ORDER BY e.pc_principal DESC) AS ordem
  FROM data_glow_up.gold.emenda_mun_senador e
  JOIN data_glow_up.gold.voto_mun_senador v USING (id_senador, id_municipio)
  JOIN data_glow_up.bronze.municipio m USING (id_municipio)
  WHERE e.populacao > 10000
)
SELECT
  t.id_senador,
  s.sigla_uf,
  s.nome_parlamentar,
  t.n,
  ROUND(t.rho, 3) AS rho,
  ROUND(t.p_valor, 4) AS p_valor,
  ROUND(t.rho_placebo_emenda_outros, 3) AS rho_placebo_emenda_outros,
  mun.id_municipio,
  mun.municipio,
  mun.populacao,
  ROUND(mun.pc_principal, 2) AS rs_por_habitante,
  ROUND(mun.pct_votos, 2) AS pct_votos_2026
FROM escolhido t
JOIN data_glow_up.gold.senador_regras s USING (id_senador)
JOIN mun ON mun.id_senador = t.id_senador AND mun.ordem = 1;
