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
spark.createDataFrame(res).write.mode("overwrite").option("overwriteSchema", "true").saveAsTable("data_glow_up.gold.correlacao_pvalor")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Robustez (cenário principal)
# MAGIC - **Parcial:** Spearman entre X e Y controlando pela população (correlação parcial sobre os postos; t com n − 3 g.l.).
# MAGIC - **Ponderado:** Pearson ponderado pelos votos válidos para Senador sobre os postos (proxy do eleitorado; sem valor-p).
# MAGIC - **Placebo 1 — emenda dos outros:** X trocado pelas emendas per capita de todos os outros autores para o município, contra o voto do senador.
# MAGIC - **Placebo 2 — voto dos outros:** X do senador contra o % de cada outro candidato a Senador da UF (mediana dos ρ).
# MAGIC   Referência fraca: os % de um município somam 200%, então há viés mecânico para ρ negativo.

# COMMAND ----------

import numpy as np
from scipy.stats import rankdata, t as dist_t


def parcial(x, y, z):
    rx, ry, rz = rankdata(x), rankdata(y), rankdata(z)
    rxy, rxz, ryz = np.corrcoef(rx, ry)[0, 1], np.corrcoef(rx, rz)[0, 1], np.corrcoef(ry, rz)[0, 1]
    r = (rxy - rxz * ryz) / np.sqrt((1 - rxz**2) * (1 - ryz**2))
    gl = len(x) - 3
    estat = r * np.sqrt(gl / (1 - r**2))
    return float(r), float(2 * dist_t.sf(abs(estat), gl))


def ponderado(x, y, w):
    # Pearson ponderado sobre os postos (Spearman ponderado); sem valor-p padrão
    rx, ry, w = rankdata(x), rankdata(y), np.asarray(w, dtype=float)
    mx, my = np.average(rx, weights=w), np.average(ry, weights=w)
    cov = np.average((rx - mx) * (ry - my), weights=w)
    return float(cov / np.sqrt(np.average((rx - mx) ** 2, weights=w) * np.average((ry - my) ** 2, weights=w)))


mun = spark.sql("""
    SELECT e.id_senador, e.id_municipio, e.populacao, e.pc_principal, e.pc_outros, v.pct_votos, v.votos_validos_senador
    FROM data_glow_up.gold.emenda_mun_senador e
    JOIN data_glow_up.gold.voto_mun_senador v USING (id_senador, id_municipio)
""").toPandas()
outros = spark.sql("""
    SELECT s.id_senador, v.id_municipio, v.sq_candidato,
           v.votos_validos / SUM(v.votos_validos) OVER (PARTITION BY v.id_municipio) * 100 AS pct_votos
    FROM data_glow_up.silver.senador s
    JOIN data_glow_up.silver.voto_municipio v ON v.sigla_uf = s.sigla_uf
""").toPandas()
outros = outros[outros["sq_candidato"] != outros["id_senador"].map(
    spark.table("data_glow_up.silver.senador").toPandas().set_index("id_senador")["sq_candidato"])]
for df in (mun, outros):
    for c in ["populacao", "pc_principal", "pc_outros", "pct_votos", "votos_validos_senador"]:
        if c in df:
            df[c] = df[c].astype(float)

linhas = []
for id_senador, g in mun.groupby("id_senador"):
    if len(g) < 4 or g["pc_principal"].nunique() < 2:
        continue
    rho, p = spearmanr(g["pc_principal"], g["pct_votos"])
    rho_parcial, p_parcial = parcial(g["pc_principal"], g["pct_votos"], g["populacao"])
    rho_ponderado = ponderado(g["pc_principal"], g["pct_votos"], g["votos_validos_senador"])
    rho_outros, p_outros = spearmanr(g["pc_outros"], g["pct_votos"])
    x = g.set_index("id_municipio")["pc_principal"]
    rhos_votos = [
        spearmanr(x.loc[o["id_municipio"]], o["pct_votos"])[0]
        for _, o in outros[(outros["id_senador"] == id_senador) & outros["id_municipio"].isin(x.index)].groupby("sq_candidato")
    ]
    linhas.append((id_senador, len(g), float(rho), float(p), rho_parcial, p_parcial, rho_ponderado,
                   float(rho_outros), float(p_outros), float(np.nanmedian(rhos_votos)), len(rhos_votos)))

rob = pd.DataFrame(linhas, columns=[
    "id_senador", "n", "rho", "p_valor", "rho_parcial_pop", "p_parcial_pop", "rho_ponderado_votos",
    "rho_placebo_emenda_outros", "p_placebo_emenda_outros", "rho_placebo_voto_outros_mediana", "n_outros_candidatos",
])
spark.createDataFrame(rob).write.mode("overwrite").option("overwriteSchema", "true").saveAsTable("data_glow_up.gold.robustez_senador")

# COMMAND ----------

# Conferência: diferença máxima entre o ρ do SQL (4 casas) e o do scipy
display(spark.sql("""
    SELECT COUNT(*) AS pares, MAX(ABS(c.rho - p.rho_scipy)) AS maior_diferenca
    FROM data_glow_up.gold.correlacao_senador c
    JOIN data_glow_up.gold.correlacao_pvalor p USING (id_senador, cenario)
"""))
