# Databricks notebook source
# MAGIC %md
# MAGIC # 05 — Eleição de 2018
# MAGIC Votação para Senador em 2018 (TSE, `ingest/bronze_2018.py`) contra a emenda per capita do cenário principal.
# MAGIC - `gold.voto_mun_senador_2018`: % dos votos válidos para Senador em 2018 no município (mesma definição de 2026).
# MAGIC - `gold.correlacao_2018`: por senador, ρ(emenda per capita × % 2018) e ρ(emenda per capita × variação 2018→2026,
# MAGIC   em pontos percentuais), com n e valor-p (`scipy.stats.spearmanr`, bicaudal).
# MAGIC
# MAGIC Só a eleição ordinária de 2018 (`cd_eleicao` = 297); a suplementar de MT (2020) fica fora.
# MAGIC Quem não foi candidato a Senador titular em 2018 (ex.: 1º suplente) fica sem linha.

# COMMAND ----------

spark.sql("""
    CREATE OR REPLACE TABLE data_glow_up.bronze.votacao_senador_munzona_2018 AS
    SELECT * FROM read_files('/Volumes/data_glow_up/bronze/arquivos/votacao_senador_munzona_2018.parquet')
""")
spark.sql("""
    CREATE OR REPLACE TABLE data_glow_up.bronze.senador_2018 AS
    SELECT * FROM read_files('/Volumes/data_glow_up/bronze/arquivos/senador_2018.parquet')
""")

# COMMAND ----------

# Votação 2018: soma as zonas; código TSE -> IBGE pelo diretório, como em 02_silver.sql
spark.sql("""
    CREATE OR REPLACE TABLE data_glow_up.silver.voto_municipio_2018 AS
    SELECT
      m.id_municipio,
      v.sg_uf AS sigla_uf,
      v.sq_candidato,
      v.nm_urna_candidato,
      SUM(CAST(v.qt_votos_nominais_validos AS BIGINT)) AS votos_validos
    FROM data_glow_up.bronze.votacao_senador_munzona_2018 v
    JOIN data_glow_up.bronze.municipio m ON CAST(v.cd_municipio AS INT) = CAST(m.id_municipio_tse AS INT)
    WHERE v.cd_eleicao = '297' AND v.nr_turno = '1'
    GROUP BY ALL
""")

# COMMAND ----------

spark.sql("""
    CREATE OR REPLACE TABLE data_glow_up.gold.voto_mun_senador_2018 AS
    WITH total AS (
      SELECT id_municipio, SUM(votos_validos) AS votos_validos_senador
      FROM data_glow_up.silver.voto_municipio_2018
      GROUP BY id_municipio
    )
    SELECT
      s.id_senador,
      v.id_municipio,
      v.votos_validos AS votos_senador_2018,
      t.votos_validos_senador AS votos_validos_senador_2018,
      v.votos_validos / t.votos_validos_senador * 100 AS pct_votos_2018
    FROM data_glow_up.bronze.senador_2018 s
    JOIN data_glow_up.silver.voto_municipio_2018 v ON v.sq_candidato = s.sq_candidato_2018
    JOIN total t USING (id_municipio)
    WHERE s.ds_cargo = 'SENADOR'
""")

# COMMAND ----------

import pandas as pd
from scipy.stats import spearmanr

base = spark.sql("""
    SELECT e.id_senador, e.pc_principal, v.pct_votos, o.pct_votos_2018
    FROM data_glow_up.gold.emenda_mun_senador e
    JOIN data_glow_up.gold.voto_mun_senador v USING (id_senador, id_municipio)
    JOIN data_glow_up.gold.voto_mun_senador_2018 o USING (id_senador, id_municipio)
""").toPandas()
for c in ["pc_principal", "pct_votos", "pct_votos_2018"]:
    base[c] = base[c].astype(float)
base["variacao_pp"] = base["pct_votos"] - base["pct_votos_2018"]

linhas = []
for id_senador, g in base.groupby("id_senador"):
    if len(g) < 3 or g["pc_principal"].nunique() < 2:
        continue
    r18, p18 = spearmanr(g["pc_principal"], g["pct_votos_2018"])
    rva, pva = spearmanr(g["pc_principal"], g["variacao_pp"])
    linhas.append((id_senador, len(g), float(r18), float(p18), float(rva), float(pva)))

res = pd.DataFrame(linhas, columns=["id_senador", "n", "rho_voto_2018", "p_voto_2018", "rho_variacao", "p_variacao"])
spark.createDataFrame(res).write.mode("overwrite").option("overwriteSchema", "true").saveAsTable("data_glow_up.gold.correlacao_2018")
