-- Eleição de 2018, senadores do ranking: ρ(emenda per capita × % dos votos válidos 2018) e
-- ρ(emenda per capita × variação do % 2018→2026, em p.p.), com n e valor-p. ρ 2026 ao lado para comparação.
-- Sem candidatura a Senador titular na eleição ordinária de 2018 → colunas de 2018 vazias.
SELECT
  s.sigla_uf,
  s.nome_parlamentar,
  s.sigla_partido,
  s.situacao_2026,
  coalesce(c18.ds_cargo, 'sem candidatura em 2018') AS cargo_2018,
  c18.ds_sit_tot_turno AS situacao_2018,
  r.n AS n_2026,
  ROUND(r.rho, 3) AS rho_2026,
  ROUND(r.p_valor, 4) AS p_2026,
  o.n AS n_2018,
  ROUND(o.rho_voto_2018, 3) AS rho_voto_2018,
  ROUND(o.p_voto_2018, 4) AS p_voto_2018,
  ROUND(o.rho_variacao, 3) AS rho_variacao,
  ROUND(o.p_variacao, 4) AS p_variacao
FROM data_glow_up.gold.senador_regras s
JOIN data_glow_up.gold.robustez_senador r USING (id_senador)
LEFT JOIN data_glow_up.gold.correlacao_2018 o USING (id_senador)
-- Uma linha por senador: a candidatura da eleição ordinária (a suplementar de MT 2020 e a suplência inapta de TO ficam fora)
LEFT JOIN (
  SELECT DISTINCT b.id_senador, b.ds_cargo, b.ds_sit_tot_turno
  FROM data_glow_up.bronze.senador_2018 b
  WHERE b.sq_candidato_2018 IN (SELECT sq_candidato FROM data_glow_up.silver.voto_municipio_2018)
     OR (b.ds_cargo <> 'SENADOR' AND b.ds_situacao_candidatura = 'APTO')
) c18 USING (id_senador)
WHERE s.no_ranking
ORDER BY o.rho_voto_2018 DESC NULLS LAST;
