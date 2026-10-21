-- Databricks notebook source
-- MAGIC %md
-- MAGIC # 02 — Silver
-- MAGIC Dados limpos e com código IBGE do município. Regras: `PRD.md` seção 7 e `METODOLOGIA.md`.
-- MAGIC - `senador`: os 32 senadores que tentaram a reeleição, com as chaves do TSE e do Portal da Transparência.
-- MAGIC - `emenda_senador`: emendas individuais dos 32, ano da emenda 2020–2026, pagamentos até 09/2026, todos os favorecidos.
-- MAGIC - `voto_municipio`: votos válidos por candidato a Senador e município (zonas somadas).
-- MAGIC - `populacao`: população municipal IBGE 2025.

-- COMMAND ----------

-- Nome normalizado para casar municípios: maiúsculas, sem acento, espaços simples (igual a norm() em ingest/)
CREATE OR REPLACE FUNCTION data_glow_up.silver.norm(s STRING) RETURNS STRING
RETURN regexp_replace(trim(translate(upper(s), 'ÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇÑ', 'AAAAAEEEEIIIIOOOOOUUUUCN')), '\\s+', ' ');

-- COMMAND ----------

CREATE OR REPLACE TABLE data_glow_up.silver.senador AS
SELECT
  id_senador,
  sq_candidato,
  codigo_do_autor_da_emenda AS codigo_autor,
  sigla_uf,
  nome_parlamentar,
  sigla_partido,
  titular_suplente,
  ds_sit_tot_turno AS situacao_2026
FROM data_glow_up.bronze.senador_reeleicao;

-- COMMAND ----------

-- Municípios do Portal da Transparência com nome antigo (renomeados), conferidos no diretório em 20/10/2026
CREATE OR REPLACE TABLE data_glow_up.silver.depara_municipio_nome AS
SELECT * FROM VALUES
  ('MG', 'BRASOPOLIS', '3108909'),             -- Brazópolis
  ('PA', 'ELDORADO DOS CARAJAS', '1502954'),   -- Eldorado do Carajás
  ('PB', 'SERIDO', '2515401'),                 -- São Vicente do Seridó
  ('RJ', 'TRAJANO DE MORAIS', '3305901'),      -- Trajano de Moraes
  ('RN', 'AUGUSTO SEVERO', '2401305'),         -- Campo Grande
  ('RN', 'JANUARIO CICCO', '2405306'),         -- Boa Saúde
  ('RN', 'PRESIDENTE JUSCELINO', '2410306'),   -- Serra Caiada
  ('RS', 'SANTANA DO LIVRAMENTO', '4317103'),  -- Sant'Ana do Livramento
  ('SP', 'EMBU', '3515004')                    -- Embu das Artes
AS t(sigla_uf, nome_norm, id_municipio);

-- COMMAND ----------

CREATE OR REPLACE TABLE data_glow_up.silver.emenda_senador AS
WITH em AS (
  SELECT
    e.codigo_da_emenda AS codigo_emenda,
    try_cast(left(e.codigo_da_emenda, 4) AS INT) AS ano_emenda,
    e.tipo_de_emenda AS tipo_emenda,
    e.ano_mes,
    s.id_senador,
    s.sigla_uf AS uf_senador,
    e.codigo_do_favorecido AS codigo_favorecido,
    e.favorecido,
    e.natureza_juridica,
    e.uf_favorecido,
    e.municipio_favorecido,
    -- Critério: só conta para o município quando o favorecido é o próprio ente municipal
    e.natureza_juridica IN (
      'Município',
      'Fundo Público da Administração Direta Municipal',
      'Órgão Público do Poder Executivo Municipal'
    ) AS ente_municipal,
    CAST(replace(e.valor_recebido, ',', '.') AS DECIMAL(18, 2)) AS valor
  FROM data_glow_up.bronze.emenda_favorecido e
  JOIN data_glow_up.silver.senador s ON e.codigo_do_autor_da_emenda = s.codigo_autor
  WHERE e.tipo_de_emenda LIKE '%Individual%'
    AND try_cast(left(e.codigo_da_emenda, 4) AS INT) BETWEEN 2020 AND 2026
    AND e.ano_mes <= '202609'
),
dir AS (
  SELECT sigla_uf, data_glow_up.silver.norm(nome) AS nome_norm, id_municipio
  FROM data_glow_up.bronze.municipio
)
SELECT
  em.*,
  CASE WHEN em.ente_municipal THEN coalesce(dir.id_municipio, dp.id_municipio) END AS id_municipio
FROM em
LEFT JOIN dir
  ON em.uf_favorecido = dir.sigla_uf AND data_glow_up.silver.norm(em.municipio_favorecido) = dir.nome_norm
LEFT JOIN data_glow_up.silver.depara_municipio_nome dp
  ON em.uf_favorecido = dp.sigla_uf AND data_glow_up.silver.norm(em.municipio_favorecido) = dp.nome_norm;

-- COMMAND ----------

-- Emendas individuais de ente municipal de TODOS os autores (base do placebo "emenda dos outros parlamentares")
CREATE OR REPLACE TABLE data_glow_up.silver.emenda_municipal_todos AS
WITH em AS (
  SELECT
    e.codigo_do_autor_da_emenda AS codigo_autor,
    e.tipo_de_emenda AS tipo_emenda,
    e.ano_mes,
    e.uf_favorecido,
    e.municipio_favorecido,
    CAST(replace(e.valor_recebido, ',', '.') AS DECIMAL(18, 2)) AS valor
  FROM data_glow_up.bronze.emenda_favorecido e
  WHERE e.tipo_de_emenda LIKE '%Individual%'
    AND try_cast(left(e.codigo_da_emenda, 4) AS INT) BETWEEN 2020 AND 2026
    AND e.ano_mes <= '202609'
    AND e.natureza_juridica IN (
      'Município',
      'Fundo Público da Administração Direta Municipal',
      'Órgão Público do Poder Executivo Municipal'
    )
),
dir AS (
  SELECT sigla_uf, data_glow_up.silver.norm(nome) AS nome_norm, id_municipio
  FROM data_glow_up.bronze.municipio
)
SELECT em.*, coalesce(dir.id_municipio, dp.id_municipio) AS id_municipio
FROM em
LEFT JOIN dir
  ON em.uf_favorecido = dir.sigla_uf AND data_glow_up.silver.norm(em.municipio_favorecido) = dir.nome_norm
LEFT JOIN data_glow_up.silver.depara_municipio_nome dp
  ON em.uf_favorecido = dp.sigla_uf AND data_glow_up.silver.norm(em.municipio_favorecido) = dp.nome_norm;

-- COMMAND ----------

-- Votação: soma as zonas; CD_MUNICIPIO é código TSE -> id_municipio (IBGE) pelo diretório
CREATE OR REPLACE TABLE data_glow_up.silver.voto_municipio AS
SELECT
  m.id_municipio,
  v.sg_uf AS sigla_uf,
  v.sq_candidato,
  v.nm_urna_candidato,
  v.sg_partido,
  v.ds_sit_tot_turno AS situacao_2026,
  SUM(CAST(v.qt_votos_nominais_validos AS BIGINT)) AS votos_validos
FROM data_glow_up.bronze.votacao_senador_munzona v
JOIN data_glow_up.bronze.municipio m ON CAST(v.cd_municipio AS INT) = CAST(m.id_municipio_tse AS INT)
WHERE v.nr_turno = '1'
GROUP BY ALL;

-- COMMAND ----------

-- Correção de fonte: em 2025 há 1 linha sem código e sem UF (5.877 hab.) e Boa Esperança do Norte/MT (5101837),
-- município novo, é o único do diretório sem população. A linha é atribuída a ele (decisão de 20/10/2026).
CREATE OR REPLACE TABLE data_glow_up.silver.populacao AS
SELECT
  coalesce(id_municipio, '5101837') AS id_municipio,
  coalesce(sigla_uf, 'MT') AS sigla_uf,
  CAST(populacao AS BIGINT) AS populacao
FROM data_glow_up.bronze.populacao
WHERE ano = '2025';

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Conferências

-- COMMAND ----------

-- Emendas: esperado R$ 8,74 bi individuais e R$ 4,64 bi de ente municipal na UF (ingest/senadores_reeleicao.py)
SELECT
  COUNT(*) AS linhas,
  ROUND(SUM(valor) / 1e9, 2) AS rs_individual_bi,
  ROUND(SUM(CASE WHEN ente_municipal AND uf_favorecido = uf_senador THEN valor END) / 1e9, 2) AS rs_municipal_uf_bi,
  SUM(CASE WHEN ente_municipal AND id_municipio IS NULL THEN 1 ELSE 0 END) AS municipal_sem_codigo,
  ROUND(SUM(CASE WHEN ente_municipal AND id_municipio IS NULL THEN valor ELSE 0 END), 2) AS rs_municipal_sem_codigo
FROM data_glow_up.silver.emenda_senador;

-- Todos os autores: linhas sem código IBGE (esperado 0) e R$ total
SELECT COUNT(*) AS linhas, ROUND(SUM(valor) / 1e9, 2) AS rs_bi,
  SUM(CASE WHEN id_municipio IS NULL THEN 1 ELSE 0 END) AS sem_codigo,
  ROUND(SUM(CASE WHEN id_municipio IS NULL THEN valor ELSE 0 END), 2) AS rs_sem_codigo
FROM data_glow_up.silver.emenda_municipal_todos;

-- Municípios distintos por senador: por código IBGE (silver) x por nome (bronze, contagem do script Python)
SELECT s.sigla_uf, s.nome_parlamentar, b.n_municipios AS n_por_nome, COUNT(DISTINCT e.id_municipio) AS n_por_codigo
FROM data_glow_up.silver.senador s
JOIN data_glow_up.bronze.senador_reeleicao b USING (id_senador)
LEFT JOIN data_glow_up.silver.emenda_senador e
  ON e.id_senador = s.id_senador AND e.ente_municipal AND e.uf_favorecido = e.uf_senador
GROUP BY ALL
HAVING CAST(replace(b.n_municipios, ',', '.') AS DOUBLE) <> COUNT(DISTINCT e.id_municipio);

-- Votos: esperado 207.038.240 válidos para Senador, 5.571 municípios e os 32 senadores presentes
SELECT
  SUM(votos_validos) AS votos_validos,
  COUNT(DISTINCT id_municipio) AS municipios,
  COUNT(DISTINCT CASE WHEN sq_candidato IN (SELECT sq_candidato FROM data_glow_up.silver.senador) THEN sq_candidato END) AS senadores_32
FROM data_glow_up.silver.voto_municipio;

-- População 2025: esperado 5.571 municípios, 213.421.037 habitantes e todos presentes no diretório
SELECT COUNT(*) AS municipios, SUM(populacao) AS populacao,
  COUNT(*) - COUNT(m.id_municipio) AS fora_do_diretorio
FROM data_glow_up.silver.populacao p
LEFT JOIN data_glow_up.bronze.municipio m USING (id_municipio);
