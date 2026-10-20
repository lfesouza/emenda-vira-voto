"""Senadores do mandato 2019/2027 que concorreram em 2026 e suas emendas por município.

Uso (na raiz do repositório):
    .venv/Scripts/python ingest/senadores_reeleicao.py data/tse_cand/consulta_cand_2026.zip data/portal/EmendasParlamentares.zip

Saída: tabela no terminal e data/senadores_reeleicao.csv (fora do git).
"""
import sys
import unicodedata
import zipfile
from pathlib import Path

import basedosdados as bd
import pandas as pd

pd.set_option("display.width", 250)
pd.set_option("display.max_rows", 200)

env = dict(
    linha.split("=", 1)
    for linha in Path(".env").read_text().splitlines()
    if "=" in linha and not linha.startswith("#")
)
projeto = env["GCP_BILLING_PROJECT"]
ENTE_MUNICIPAL = [
    "Município",
    "Fundo Público da Administração Direta Municipal",
    "Órgão Público do Poder Executivo Municipal",
]


def norm(s):
    return " ".join(unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().upper().split())


# 1. Senadores em exercício com mandato 2019/2027 (vagas em disputa em 2026)
sen = bd.read_sql(
    """
    SELECT id_senador, nome_parlamentar, nome_completo, sigla_uf, sigla_partido, titular_suplente
    FROM `basedosdados.br_senado_dados_abertos_administrativos.senador`
    WHERE indicador_em_exercicio = 'sim' AND mandato = '2019 / 2027'
    """,
    billing_project_id=projeto,
)
print("Senadores em exercício, mandato 2019/2027:", len(sen))

# 2. Candidatos a Senador em 2026 (TSE)
z = zipfile.ZipFile(sys.argv[1])
cand = pd.read_csv(z.open("consulta_cand_2026_BRASIL.csv"), sep=";", encoding="latin-1", dtype=str)
cand = cand[cand["DS_CARGO"].str.upper() == "SENADOR"]

sen["k_completo"] = sen["sigla_uf"] + "|" + sen["nome_completo"].map(norm)
sen["k_urna"] = sen["sigla_uf"] + "|" + sen["nome_parlamentar"].map(norm)
cand["k_completo"] = cand["SG_UF"] + "|" + cand["NM_CANDIDATO"].map(norm)
cand["k_urna"] = cand["SG_UF"] + "|" + cand["NM_URNA_CANDIDATO"].map(norm)

m1 = sen.merge(cand, on="k_completo", suffixes=("", "_tse"))
resto = sen[~sen["id_senador"].isin(m1["id_senador"])]
m2 = resto.merge(cand, on="k_urna", suffixes=("", "_tse"))
m1["casamento"], m2["casamento"] = "nome completo", "nome de urna"
casados = pd.concat([m1, m2], ignore_index=True)
print("Casados com candidatura 2026:", len(casados), casados["casamento"].value_counts().to_dict())
print("Situação TSE:", casados["DS_SIT_TOT_TURNO"].value_counts().to_dict())

# Conferência: candidatos que declararam ocupação de senador e não casaram
ocup = cand[cand["DS_OCUPACAO"].str.contains("SENADOR", case=False, na=False)]
sobra = ocup[~ocup["SQ_CANDIDATO"].isin(casados["SQ_CANDIDATO"])]
print("Ocupação 'senador' no TSE:", len(ocup), "| sem casamento:", len(sobra))
if len(sobra):
    print(sobra[["SG_UF", "NM_URNA_CANDIDATO", "DS_OCUPACAO"]].to_string(index=False))

# 3. Emendas por favorecido: individuais, ano da emenda 2020-2026 (apresentadas durante o mandato), pagas até 09/2026
z = zipfile.ZipFile(sys.argv[2])
em = pd.read_csv(z.open("EmendasParlamentares_PorFavorecido.csv"), sep=";", encoding="latin-1", dtype=str)
em["valor"] = em["Valor Recebido"].str.replace(",", ".").astype(float)
em["ano"] = pd.to_numeric(em["Código da Emenda"].str[:4], errors="coerce")
em = em[em["Tipo de Emenda"].str.contains("Individual") & em["ano"].between(2020, 2026) & (em["Ano/Mês"] <= "202609")]

# Autor da emenda -> senador, por nome parlamentar normalizado
autores = em[["Código do Autor da Emenda", "Nome do Autor da Emenda"]].drop_duplicates()
autores["k_nome"] = autores["Nome do Autor da Emenda"].map(norm)
casados["k_nome"] = casados["nome_parlamentar"].map(norm)
aut = casados[["id_senador", "k_nome"]].merge(autores, on="k_nome", how="left")
print("\nAutores por senador (esperado 1):", aut.groupby("id_senador")["Código do Autor da Emenda"].nunique().value_counts().to_dict())
sem_autor = casados[~casados["id_senador"].isin(aut.dropna()["id_senador"])]
if len(sem_autor):
    print("Sem autor casado:", sem_autor[["sigla_uf", "nome_parlamentar"]].to_string(index=False))

em = em.merge(aut.dropna()[["id_senador", "Código do Autor da Emenda"]], on="Código do Autor da Emenda")
em = em.merge(casados[["id_senador", "sigla_uf"]], on="id_senador")
em["municipal"] = em["Natureza Jurídica"].isin(ENTE_MUNICIPAL)
em["no_estado"] = em["UF Favorecido"] == em["sigla_uf"]

mun = em[em["municipal"] & em["no_estado"]]
res = casados[["id_senador", "SQ_CANDIDATO", "sigla_uf", "nome_parlamentar", "sigla_partido", "titular_suplente", "DS_SIT_TOT_TURNO", "casamento"]].copy()
res = res.merge(aut.dropna()[["id_senador", "Código do Autor da Emenda"]], on="id_senador", how="left")
res = res.merge(em.groupby("id_senador")["valor"].sum().rename("rs_individual"), on="id_senador", how="left")
res = res.merge(mun.groupby("id_senador")["valor"].sum().rename("rs_municipal_uf"), on="id_senador", how="left")
res = res.merge(
    em[em["municipal"] & ~em["no_estado"]].groupby("id_senador")["valor"].sum().rename("rs_municipal_outra_uf"),
    on="id_senador", how="left",
)
res = res.merge(mun.groupby("id_senador")["Município Favorecido"].nunique().rename("n_municipios"), on="id_senador", how="left")
res = res.fillna({"rs_individual": 0, "rs_municipal_uf": 0, "rs_municipal_outra_uf": 0, "n_municipios": 0})
res["cobertura_pct"] = (res["rs_municipal_uf"] / res["rs_individual"] * 100).round(1)
# Regras de entrada no ranking: fora o DF, mínimo de 15 municípios e cobertura de 20%+
res["minimo_15"] = (res["n_municipios"] >= 15) & (res["sigla_uf"] != "DF")
res["cobertura_20"] = res["cobertura_pct"] >= 20
res["no_ranking"] = res["minimo_15"] & res["cobertura_20"]
res = res.sort_values(["sigla_uf", "nome_parlamentar"])
# Formato do Excel em português: separador ;, vírgula decimal, UTF-8 com BOM
res.to_csv("data/senadores_reeleicao.csv", index=False, sep=";", decimal=",", encoding="utf-8-sig")

out = res.drop(columns=["id_senador", "SQ_CANDIDATO", "Código do Autor da Emenda"]).copy()
for c in ["rs_individual", "rs_municipal_uf", "rs_municipal_outra_uf"]:
    out[c] = (out[c] / 1e6).round(1)
print("\nValores em R$ milhões:")
print(out.to_string(index=False))
print(
    f"\nTotal: {len(res)} senadores | mínimo de 15 municípios: {res['minimo_15'].sum()} | "
    f"cobertura 20%+: {res['cobertura_20'].sum()} | no ranking: {res['no_ranking'].sum()} | "
    f"R$ individual {res['rs_individual'].sum() / 1e9:.2f} bi | R$ municipal na UF {res['rs_municipal_uf'].sum() / 1e9:.2f} bi"
)
