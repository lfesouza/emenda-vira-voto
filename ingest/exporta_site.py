"""Exporta os dados da página: roda cada query de sql/gold/ no Databricks e grava site/data/<query>.json.
Também baixa a malha municipal do IBGE (qualidade mínima) de cada UF para site/data/geo/.

Uso (na raiz do repositório, com login feito em `databricks auth login`):
    .venv/Scripts/python ingest/exporta_site.py
"""
import gzip
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

env = dict(
    linha.split("=", 1)
    for linha in Path(".env").read_text().splitlines()
    if "=" in linha and not linha.startswith("#")
)
WAREHOUSE = env["DATABRICKS_WAREHOUSE_ID"]
saida = Path("site/data")
(saida / "geo").mkdir(parents=True, exist_ok=True)


def api(metodo, caminho, corpo=None):
    cmd = ["databricks", "api", metodo, caminho] + (["--json", json.dumps(corpo)] if corpo else [])
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if r.returncode:
        sys.exit(r.stderr)
    return json.loads(r.stdout)


def consulta(sql):
    r = api("post", "/api/2.0/sql/statements", {
        "warehouse_id": WAREHOUSE, "statement": sql, "wait_timeout": "50s",
        "disposition": "INLINE", "format": "JSON_ARRAY",
    })
    while r["status"]["state"] in ("PENDING", "RUNNING"):
        time.sleep(3)
        r = api("get", f"/api/2.0/sql/statements/{r['statement_id']}")
    if r["status"]["state"] != "SUCCEEDED":
        sys.exit(f"Erro na consulta: {r['status']}")
    colunas = [(c["name"], c["type_name"]) for c in r["manifest"]["schema"]["columns"]]
    linhas = list(r["result"].get("data_array", []))
    # Resultados grandes vêm em partes
    proximo = r["result"].get("next_chunk_internal_link")
    while proximo:
        parte = api("get", proximo)
        linhas += parte.get("data_array", [])
        proximo = parte.get("next_chunk_internal_link")

    def valor(v, tipo):
        if v is None:
            return None
        if tipo in ("INT", "LONG", "BIGINT", "SHORT"):
            return int(v)
        if tipo in ("DOUBLE", "FLOAT", "DECIMAL"):
            return float(v)
        if tipo == "BOOLEAN":
            return v == "true"
        return v

    return [{n: valor(v, t) for (n, t), v in zip(colunas, linha)} for linha in linhas]


for arquivo in sorted(Path("sql/gold").glob("*.sql")):
    dados = consulta(arquivo.read_text(encoding="utf-8").strip().rstrip(";"))
    (saida / f"{arquivo.stem}.json").write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    print(f"{arquivo.name}: {len(dados)} linhas")

ufs = sorted({s["sigla_uf"] for s in json.loads((saida / "04_ranking.json").read_text(encoding="utf-8"))} - {"DF"})
for uf in ufs:
    destino = saida / "geo" / f"{uf}.json"
    if not destino.exists():
        url = (f"https://servicodados.ibge.gov.br/api/v3/malhas/estados/{uf}"
               "?formato=application/vnd.geo+json&qualidade=minima&intrarregiao=municipio")
        conteudo = urllib.request.urlopen(url).read()
        # A API do IBGE responde comprimida em gzip
        if conteudo[:2] == bytes([0x1F, 0x8B]):
            conteudo = gzip.decompress(conteudo)
        destino.write_bytes(conteudo)
print("Malhas IBGE:", len(ufs), "UFs em", saida / "geo")
