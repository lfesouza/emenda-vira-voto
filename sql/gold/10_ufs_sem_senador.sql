-- UFs sem nenhum senador entre os 32 que tentaram a reeleição em 2026.
SELECT DISTINCT m.sigla_uf, m.nome_uf
FROM data_glow_up.bronze.municipio m
WHERE m.sigla_uf NOT IN (SELECT sigla_uf FROM data_glow_up.gold.senador_regras)
ORDER BY m.sigla_uf;
