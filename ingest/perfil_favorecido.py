"""Perfil do arquivo do Portal da Transparência "EmendasParlamentares_PorFavorecido.csv".

Uso (na raiz do repositório):
    .venv/Scripts/python ingest/perfil_favorecido.py data/portal/EmendasParlamentares.zip
"""
import sys
import zipfile

import pandas as pd

pd.set_option("display.width", 250)
pd.set_option("display.max_rows", 200)

with zipfile.ZipFile(sys.argv[1]).open("EmendasParlamentares_PorFavorecido.csv") as f:
    df = pd.read_csv(f, sep=";", encoding="latin-1", dtype=str)

df["valor"] = df["Valor Recebido"].str.replace(".", "", regex=False).str.replace(",", ".").astype(float)
# Ano da emenda = 4 primeiros dígitos do código (mesmo critério de ano_emenda da Base dos Dados)
df["ano_emenda"] = pd.to_numeric(df["Código da Emenda"].str[:4], errors="coerce")
df["ano_pagamento"] = pd.to_numeric(df["Ano/Mês"].str[:4], errors="coerce")

print("Linhas no arquivo:", len(df))
print("Ano/Mês de pagamento:", df["Ano/Mês"].min(), "a", df["Ano/Mês"].max())
print("\nTipos de emenda (R$ bi, todo o arquivo):")
print((df.groupby("Tipo de Emenda")["valor"].sum() / 1e9).round(2).sort_values(ascending=False).to_string())

ind = df[df["Tipo de Emenda"].str.contains("Individual", na=False) & df["ano_emenda"].between(2019, 2026)]
print(f"\nIndividuais, ano da emenda 2019-2026: {len(ind)} linhas, R$ {ind['valor'].sum() / 1e9:.2f} bi")
print("\nNatureza Jurídica do favorecido (R$ bi):")
nat = ind.groupby("Natureza Jurídica")["valor"].agg(["count", "sum"])
nat["sum"] = (nat["sum"] / 1e9).round(3)
print(nat.sort_values("sum", ascending=False).to_string())

# Critério: só conta para o município quando o favorecido é o próprio ente municipal
ENTE_MUNICIPAL = [
    "Município",
    "Fundo Público da Administração Direta Municipal",
    "Órgão Público do Poder Executivo Municipal",
]
ind = ind.assign(ente_municipal=ind["Natureza Jurídica"].isin(ENTE_MUNICIPAL))
for periodo, sub in [("2019-2026", ind), ("2019-2025", ind[ind["ano_emenda"] <= 2025])]:
    tab = sub.groupby("ente_municipal")["valor"].agg(["count", "sum"])
    tab["pct"] = (tab["sum"] / tab["sum"].sum() * 100).round(1)
    tab["sum"] = (tab["sum"] / 1e9).round(2)
    print(f"\nCritério ente municipal — individuais, ano da emenda {periodo}:")
    print(tab.to_string())

print("\nPor tipo de emenda (2019-2026):")
tab = ind.groupby(["Tipo de Emenda", "ente_municipal"])["valor"].sum().unstack()
tab["pct_municipal"] = (tab[True] / tab.sum(axis=1) * 100).round(1)
print((tab / [1e9, 1e9, 1]).round(2).to_string())

sem = ind[ind["Natureza Jurídica"] == "Sociedade de Economia Mista"]
print("\nMaiores favorecidos 'Sociedade de Economia Mista':")
print((sem.groupby(["Código do Favorecido", "Favorecido"])["valor"].sum() / 1e9).round(2)
      .sort_values(ascending=False).head(5).to_string())
