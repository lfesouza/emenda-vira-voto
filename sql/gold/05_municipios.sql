-- Senador × município da UF: emenda per capita (X, cenário principal) e % dos votos válidos (Y). Base do mapa e da dispersão.
SELECT
  e.id_senador,
  e.id_municipio,
  m.nome AS municipio,
  e.populacao,
  ROUND(e.rs_principal, 2) AS rs_principal,
  ROUND(e.pc_principal, 2) AS rs_por_habitante,
  v.votos_senador,
  ROUND(v.pct_votos, 2) AS pct_votos
FROM data_glow_up.gold.emenda_mun_senador e
JOIN data_glow_up.gold.voto_mun_senador v USING (id_senador, id_municipio)
JOIN data_glow_up.bronze.municipio m USING (id_municipio)
JOIN data_glow_up.gold.senador_regras s USING (id_senador)
WHERE s.sigla_uf <> 'DF'
ORDER BY e.id_senador, e.id_municipio;
