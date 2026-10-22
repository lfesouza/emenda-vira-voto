"""Bronze 2018: votação para Senador em 2018 e o cargo que cada um dos 32 disputou em 2018.

Uso (na raiz, depois de ingest/senadores_reeleicao.py):
    .venv/Scripts/python ingest/bronze_2018.py

Casamento senador 2026 -> candidatura 2018 pelo CPF (NR_CPF_CANDIDATO) das duas consultas de candidatos do TSE.
Saída em data/bronze/: votacao_senador_munzona_2018.parquet (CD_CARGO = 5) e senador_2018.parquet.
"""
import re
import unicodedata
import zipfile
from pathlib import Path

import pandas as pd

saida = Path("data/bronze")


def coluna(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


def grava(df, nome):
    df = df.rename(columns=coluna)
    df.to_parquet(saida / f"{nome}.parquet", index=False)
    print(f"{nome}: {len(df)} linhas")


def cand(caminho, ano):
    z = zipfile.ZipFile(caminho)
    return pd.read_csv(z.open(f"consulta_cand_{ano}_BRASIL.csv"), sep=";", encoding="latin-1", dtype=str)


sen = pd.read_csv("data/senadores_reeleicao.csv", sep=";", encoding="utf-8-sig", dtype=str)
c26 = cand("data/tse_cand/consulta_cand_2026.zip", 2026)
c18 = cand("data/tse2018/consulta_cand_2018.zip", 2018)

cpf = sen[["id_senador", "SQ_CANDIDATO", "sigla_uf", "nome_parlamentar"]].merge(
    c26[["SQ_CANDIDATO", "NR_CPF_CANDIDATO"]], on="SQ_CANDIDATO")
c18 = c18[c18["NR_TURNO"] == "1"][["NR_CPF_CANDIDATO", "SG_UF", "DS_CARGO", "SQ_CANDIDATO", "NM_URNA_CANDIDATO",
                                   "DS_SITUACAO_CANDIDATURA", "DS_SIT_TOT_TURNO"]]
m = cpf.drop(columns="SQ_CANDIDATO").merge(c18, on="NR_CPF_CANDIDATO", how="left").drop(columns="NR_CPF_CANDIDATO")
print(m.to_string())
grava(m.rename(columns={"SQ_CANDIDATO": "sq_candidato_2018"}), "senador_2018")

z = zipfile.ZipFile("data/tse2018/votacao_candidato_munzona_2018.zip")
partes = pd.read_csv(z.open("votacao_candidato_munzona_2018_BRASIL.csv"), sep=";", encoding="latin-1",
                     dtype=str, chunksize=1_000_000)
grava(pd.concat(p[p["CD_CARGO"] == "5"] for p in partes), "votacao_senador_munzona_2018")
