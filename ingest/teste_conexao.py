"""Teste de conexão com a Base dos Dados (BigQuery).

Uso (na raiz do repositório):
    .venv\\Scripts\\python ingest\\teste_conexao.py

Na primeira execução o navegador abre para login com a conta Google.
Esperado: ~5.570 municípios.
"""
from pathlib import Path

import basedosdados as bd

# Lê o ID do projeto de cobrança do .env (sem dependência extra)
env = dict(
    linha.split("=", 1)
    for linha in Path(".env").read_text().splitlines()
    if "=" in linha and not linha.startswith("#")
)
projeto = env["GCP_BILLING_PROJECT"]

df = bd.read_sql(
    "SELECT COUNT(*) AS municipios FROM `basedosdados.br_bd_diretorios_brasil.municipio`",
    billing_project_id=projeto,
)
print(df)
