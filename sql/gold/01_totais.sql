-- Totais do universo: 32 senadores, R$ em emendas individuais e parte atribuível a municípios da própria UF.
-- Janela: ano da emenda 2020–2026, pagamentos até 09/2026 (METODOLOGIA.md).
SELECT
  COUNT(*) AS senadores,
  SUM(CASE WHEN situacao_2026 = 'ELEITO' THEN 1 ELSE 0 END) AS eleitos,
  SUM(CASE WHEN no_ranking THEN 1 ELSE 0 END) AS no_ranking,
  ROUND(SUM(rs_individual) / 1e9, 2) AS rs_individual_bi,
  ROUND(SUM(rs_municipal_uf) / 1e9, 2) AS rs_municipal_uf_bi,
  ROUND(SUM(rs_municipal_uf) / SUM(rs_individual) * 100, 1) AS pct_com_municipio,
  ROUND((SUM(rs_individual) - SUM(rs_municipal_uf)) / SUM(rs_individual) * 100, 1) AS pct_sem_municipio
FROM data_glow_up.gold.senador_regras;
