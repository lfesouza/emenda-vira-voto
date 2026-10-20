-- Databricks notebook source
-- MAGIC %md
-- MAGIC # 01 — Bronze
-- MAGIC Catálogo `data_glow_up`, Volume com os arquivos brutos e uma tabela por arquivo, sem transformação.
-- MAGIC Os Parquet são gerados por `ingest/bronze.py` e enviados ao Volume com:
-- MAGIC `databricks fs cp -r data/bronze dbfs:/Volumes/data_glow_up/bronze/arquivos --overwrite`

-- COMMAND ----------

CREATE CATALOG IF NOT EXISTS data_glow_up;
CREATE SCHEMA IF NOT EXISTS data_glow_up.bronze;
CREATE SCHEMA IF NOT EXISTS data_glow_up.silver;
CREATE SCHEMA IF NOT EXISTS data_glow_up.gold;
CREATE VOLUME IF NOT EXISTS data_glow_up.bronze.arquivos;

-- COMMAND ----------

-- Emendas por favorecido (Portal da Transparência)
CREATE OR REPLACE TABLE data_glow_up.bronze.emenda_favorecido AS
SELECT * FROM read_files('/Volumes/data_glow_up/bronze/arquivos/emenda_favorecido.parquet');

-- Votação TSE 2026 por município e zona, cargo Senador
CREATE OR REPLACE TABLE data_glow_up.bronze.votacao_senador_munzona AS
SELECT * FROM read_files('/Volumes/data_glow_up/bronze/arquivos/votacao_senador_munzona.parquet');

-- Diretório de municípios (Base dos Dados)
CREATE OR REPLACE TABLE data_glow_up.bronze.municipio AS
SELECT * FROM read_files('/Volumes/data_glow_up/bronze/arquivos/municipio.parquet');

-- População municipal IBGE (Base dos Dados), todos os anos
CREATE OR REPLACE TABLE data_glow_up.bronze.populacao AS
SELECT * FROM read_files('/Volumes/data_glow_up/bronze/arquivos/populacao.parquet');

-- Universo dos 32 senadores (ingest/senadores_reeleicao.py)
CREATE OR REPLACE TABLE data_glow_up.bronze.senador_reeleicao AS
SELECT * FROM read_files('/Volumes/data_glow_up/bronze/arquivos/senador_reeleicao.parquet');

-- COMMAND ----------

-- Conferência: linhas por tabela (esperado 827457, 74447, 5571, 191099, 32)
SELECT 'emenda_favorecido' AS tabela, COUNT(*) AS linhas FROM data_glow_up.bronze.emenda_favorecido
UNION ALL SELECT 'votacao_senador_munzona', COUNT(*) FROM data_glow_up.bronze.votacao_senador_munzona
UNION ALL SELECT 'municipio', COUNT(*) FROM data_glow_up.bronze.municipio
UNION ALL SELECT 'populacao', COUNT(*) FROM data_glow_up.bronze.populacao
UNION ALL SELECT 'senador_reeleicao', COUNT(*) FROM data_glow_up.bronze.senador_reeleicao;
