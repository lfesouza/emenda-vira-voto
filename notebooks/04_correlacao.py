# Databricks notebook source
# MAGIC %md
# MAGIC # 04 — Valor-p da correlação
# MAGIC Recalcula o Spearman de `gold.correlacao_senador` com `scipy.stats.spearmanr` e acrescenta o valor-p
# MAGIC (bicaudal). Grava `gold.correlacao_pvalor`. O ρ daqui deve ser igual ao do SQL (`03_gold.sql`).

# COMMAND ----------

import pandas as pd
from scipy.stats import spearmanr

base = spark.sql("""
    SELECT e.id_senador, e.pc_principal, e.pc_transf_especiais, e.pc_pagos_2026, v.pct_votos
    FROM data_glow_up.gold.emenda_mun_senador e
    JOIN data_glow_up.gold.voto_mun_senador v USING (id_senador, id_municipio)
""").toPandas().astype({"pc_principal": float, "pc_transf_especiais": float, "pc_pagos_2026": float, "pct_votos": float})

linhas = []
for id_senador, g in base.groupby("id_senador"):
    for cenario in ["principal", "transf_especiais", "pagos_2026"]:
        x = g["pc_" + cenario]
        # Com menos de 3 municípios ou X constante (ex.: DF, cenário sem emenda) a correlação não existe
        if len(g) < 3 or x.nunique() < 2:
            continue
        rho, p = spearmanr(x, g["pct_votos"])
        linhas.append((id_senador, cenario, len(g), float(rho), float(p)))

res = pd.DataFrame(linhas, columns=["id_senador", "cenario", "n", "rho_scipy", "p_valor"])
spark.createDataFrame(res).write.mode("overwrite").saveAsTable("data_glow_up.gold.correlacao_pvalor")

# COMMAND ----------

# Conferência: diferença máxima entre o ρ do SQL (4 casas) e o do scipy
display(spark.sql("""
    SELECT COUNT(*) AS pares, MAX(ABS(c.rho - p.rho_scipy)) AS maior_diferenca
    FROM data_glow_up.gold.correlacao_senador c
    JOIN data_glow_up.gold.correlacao_pvalor p USING (id_senador, cenario)
"""))
