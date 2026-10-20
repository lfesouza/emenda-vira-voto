"""Bronze: extrai as fontes brutas para Parquet, prontas para subir ao Volume do Databricks.

Uso (na raiz do repositório, depois de rodar ingest/senadores_reeleicao.py):
    .venv/Scripts/python ingest/bronze.py

Saída em data/bronze/ (fora do git). Conteúdo cru: todas as colunas como texto, só com
nomes de coluna sem acento/espaço. Único filtro: votação TSE restrita ao cargo Senador.
"""
import re
import unicodedata
import zipfile
from pathlib import Path

import basedosdados as bd
import pandas as pd

env = dict(
    linha.split("=", 1)
    for linha in Path(".env").read_text().splitlines()
    if "=" in linha and not linha.startswith("#")
)
projeto = env["GCP_BILLING_PROJECT"]
saida = Path("data/bronze")
saida.mkdir(exist_ok=True)


def coluna(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


def grava(df, nome):
    df = df.rename(columns=coluna)
    df.to_parquet(saida / f"{nome}.parquet", index=False)
    print(f"{nome}: {len(df)} linhas")


# Emendas por favorecido (Portal da Transparência, F1b)
z = zipfile.ZipFile("data/portal/EmendasParlamentares.zip")
grava(pd.read_csv(z.open("EmendasParlamentares_PorFavorecido.csv"), sep=";", encoding="latin-1", dtype=str),
      "emenda_favorecido")

# Votação TSE 2026 por município e zona (F4), só Senador (CD_CARGO = 5)
z = zipfile.ZipFile("data/tse/votacao_candidato_munzona_2026.zip")
partes = pd.read_csv(z.open("votacao_candidato_munzona_2026_BRASIL.csv"), sep=";", encoding="latin-1",
                     dtype=str, chunksize=1_000_000)
grava(pd.concat(p[p["CD_CARGO"] == "5"] for p in partes), "votacao_senador_munzona")

# Diretório de municípios (F6) e população (F5), da Base dos Dados
grava(bd.read_sql(
    """
    SELECT * EXCEPT (centroide)
    FROM `basedosdados.br_bd_diretorios_brasil.municipio`
    """,
    billing_project_id=projeto,
).astype("string"), "municipio")
grava(bd.read_sql(
    "SELECT * FROM `basedosdados.br_ibge_populacao.municipio`",
    billing_project_id=projeto,
).astype("string"), "populacao")

# Universo dos 32 senadores (gerado por ingest/senadores_reeleicao.py)
grava(pd.read_csv("data/senadores_reeleicao.csv", sep=";", encoding="utf-8-sig", dtype=str), "senador_reeleicao")
