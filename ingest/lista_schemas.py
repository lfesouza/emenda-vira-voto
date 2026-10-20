"""Lista datasets, tabelas e colunas reais da Base dos Dados usados no projeto.

Uso (na raiz do repositório):
    .venv/Scripts/python ingest/lista_schemas.py            -> lista os datasets candidatos
    .venv/Scripts/python ingest/lista_schemas.py <dataset>  -> tabelas e colunas do dataset

Consulta apenas metadados (INFORMATION_SCHEMA). Resultado vai para docs/fontes.md.
"""
import sys
from pathlib import Path

import basedosdados as bd

env = dict(
    linha.split("=", 1)
    for linha in Path(".env").read_text().splitlines()
    if "=" in linha and not linha.startswith("#")
)
projeto = env["GCP_BILLING_PROJECT"]

if len(sys.argv) == 1:
    sql = """
        SELECT schema_name
        FROM `basedosdados.region-us.INFORMATION_SCHEMA.SCHEMATA`
        WHERE REGEXP_CONTAINS(schema_name, r'senado|emenda|diretorio|populacao')
        ORDER BY schema_name
    """
else:
    dataset = sys.argv[1]
    sql = f"""
        SELECT table_name, ordinal_position, column_name, data_type
        FROM `basedosdados.{dataset}.INFORMATION_SCHEMA.COLUMNS`
        ORDER BY table_name, ordinal_position
    """

df = bd.read_sql(sql, billing_project_id=projeto)
print(df.to_string(index=False))
