-- Resultado eleitoral de 2026 dos senadores do ranking, separados pela correlação do cenário principal:
-- ρ positivo com p < 0,05 (nenhum senador tem ρ negativo com p < 0,05) × demais.
SELECT
  CASE WHEN c.rho > 0 AND p.p_valor < 0.05 THEN 'ρ positivo, p < 0,05' ELSE 'demais (p ≥ 0,05)' END AS grupo,
  COUNT(*) AS senadores,
  SUM(CASE WHEN c.situacao_2026 = 'ELEITO' THEN 1 ELSE 0 END) AS eleitos,
  SUM(CASE WHEN c.situacao_2026 = 'NÃO ELEITO' THEN 1 ELSE 0 END) AS nao_eleitos,
  ROUND(SUM(CASE WHEN c.situacao_2026 = 'ELEITO' THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) AS pct_eleitos
FROM data_glow_up.gold.correlacao_senador c
JOIN data_glow_up.gold.correlacao_pvalor p USING (id_senador, cenario)
WHERE c.cenario = 'principal' AND c.no_ranking
GROUP BY 1
ORDER BY 1 DESC;
