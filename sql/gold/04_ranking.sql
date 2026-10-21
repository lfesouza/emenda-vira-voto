-- Tabela por senador (os 32): resultado eleitoral, n, ρ e testes; motivo de quem fica fora do ranking.
SELECT
  s.id_senador,
  s.sigla_uf,
  s.nome_parlamentar,
  s.sigla_partido,
  s.situacao_2026,
  ROUND(s.rs_individual / 1e6, 1) AS rs_individual_mi,
  ROUND(s.rs_municipal_uf / 1e6, 1) AS rs_municipal_uf_mi,
  s.cobertura_pct,
  s.n_municipios_uf AS n,
  s.n_municipios_com_emenda AS n_com_emenda,
  ROUND(r.rho, 3) AS rho,
  ROUND(r.p_valor, 4) AS p_valor,
  ROUND(r.rho_parcial_pop, 3) AS rho_parcial_pop,
  ROUND(r.rho_ponderado_votos, 3) AS rho_ponderado_votos,
  ROUND(r.rho_placebo_emenda_outros, 3) AS rho_placebo_emenda_outros,
  s.no_ranking,
  CASE
    WHEN s.sigla_uf = 'DF' THEN 'DF: um único município'
    WHEN s.cobertura_pct < 20 THEN 'cobertura municipal abaixo de 20%'
    WHEN s.n_municipios_com_emenda < 15 THEN 'menos de 15 municípios com emenda'
  END AS motivo_fora
FROM data_glow_up.gold.senador_regras s
LEFT JOIN data_glow_up.gold.robustez_senador r USING (id_senador)
ORDER BY s.no_ranking DESC, r.rho DESC;
