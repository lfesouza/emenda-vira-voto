-- Resumo da eleição de 2018 (senadores do ranking com candidatura a Senador titular em 2018).
SELECT
  COUNT(*) AS senadores,
  MIN(o.n) AS n_minimo,
  MAX(o.n) AS n_maximo,
  ROUND(percentile(o.rho_voto_2018, 0.5), 3) AS rho_voto_2018_mediano,
  SUM(CASE WHEN o.rho_voto_2018 > 0 AND o.p_voto_2018 < 0.05 THEN 1 ELSE 0 END) AS voto_2018_positivo_p05,
  SUM(CASE WHEN o.rho_voto_2018 < 0 AND o.p_voto_2018 < 0.05 THEN 1 ELSE 0 END) AS voto_2018_negativo_p05,
  ROUND(percentile(o.rho_variacao, 0.5), 3) AS rho_variacao_mediano,
  SUM(CASE WHEN o.rho_variacao > 0 AND o.p_variacao < 0.05 THEN 1 ELSE 0 END) AS variacao_positivo_p05,
  SUM(CASE WHEN o.rho_variacao < 0 AND o.p_variacao < 0.05 THEN 1 ELSE 0 END) AS variacao_negativo_p05,
  ROUND(percentile(r.rho, 0.5), 3) AS rho_2026_mediano_mesmos,
  SUM(CASE WHEN r.rho > o.rho_voto_2018 THEN 1 ELSE 0 END) AS rho_2026_maior_que_2018
FROM data_glow_up.gold.correlacao_2018 o
JOIN data_glow_up.gold.robustez_senador r USING (id_senador)
JOIN data_glow_up.gold.senador_regras s USING (id_senador)
WHERE s.no_ranking;
