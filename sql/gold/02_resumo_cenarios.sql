-- Resumo da correlação de Spearman (ρ) por cenário, só senadores do ranking.
SELECT
  c.cenario,
  COUNT(*) AS senadores,
  SUM(CASE WHEN c.rho > 0 THEN 1 ELSE 0 END) AS rho_positivo,
  SUM(CASE WHEN c.rho > 0 AND p.p_valor < 0.05 THEN 1 ELSE 0 END) AS rho_positivo_p05,
  SUM(CASE WHEN c.rho < 0 AND p.p_valor < 0.05 THEN 1 ELSE 0 END) AS rho_negativo_p05,
  ROUND(percentile(c.rho, 0.5), 3) AS rho_mediano,
  MIN(c.n) AS n_minimo,
  MAX(c.n) AS n_maximo
FROM data_glow_up.gold.correlacao_senador c
JOIN data_glow_up.gold.correlacao_pvalor p USING (id_senador, cenario)
WHERE c.no_ranking
GROUP BY c.cenario
ORDER BY c.cenario;
