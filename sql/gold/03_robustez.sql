-- Resumo dos testes de robustez (cenário principal), só senadores do ranking.
SELECT
  COUNT(*) AS senadores,
  ROUND(percentile(r.rho, 0.5), 3) AS rho_mediano,
  SUM(CASE WHEN r.rho > 0 AND r.p_valor < 0.05 THEN 1 ELSE 0 END) AS rho_positivo_p05,
  ROUND(percentile(r.rho_parcial_pop, 0.5), 3) AS parcial_pop_mediano,
  SUM(CASE WHEN r.rho_parcial_pop > 0 AND r.p_parcial_pop < 0.05 THEN 1 ELSE 0 END) AS parcial_pop_positivo_p05,
  ROUND(percentile(r.rho_ponderado_votos, 0.5), 3) AS ponderado_votos_mediano,
  SUM(CASE WHEN r.rho_ponderado_votos > 0 THEN 1 ELSE 0 END) AS ponderado_votos_positivo,
  ROUND(percentile(r.rho_placebo_emenda_outros, 0.5), 3) AS placebo_emenda_outros_mediano,
  SUM(CASE WHEN r.rho_placebo_emenda_outros > 0 AND r.p_placebo_emenda_outros < 0.05 THEN 1 ELSE 0 END) AS placebo_emenda_outros_positivo_p05,
  SUM(CASE WHEN r.rho > r.rho_placebo_emenda_outros THEN 1 ELSE 0 END) AS proprio_maior_que_placebo,
  ROUND(percentile(r.rho_placebo_voto_outros_mediana, 0.5), 3) AS placebo_voto_outros_mediano
FROM data_glow_up.gold.robustez_senador r
JOIN data_glow_up.gold.senador_regras s USING (id_senador)
WHERE s.no_ranking;
