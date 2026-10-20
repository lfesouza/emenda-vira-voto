"""Perfil exploratório da tabela de emendas (define os filtros do silver).

Uso (na raiz do repositório):
    .venv/Scripts/python ingest/perfil_emendas.py
"""
from pathlib import Path

import basedosdados as bd

env = dict(
    linha.split("=", 1)
    for linha in Path(".env").read_text().splitlines()
    if "=" in linha and not linha.startswith("#")
)
projeto = env["GCP_BILLING_PROJECT"]
TABELA = "`basedosdados.br_cgu_emendas_parlamentares.microdados`"

consultas = {
    "Anos na base": f"""
        SELECT MIN(ano_emenda) AS ano_min, MAX(ano_emenda) AS ano_max, COUNT(*) AS linhas
        FROM {TABELA}
    """,
    "Tipos de emenda (2019-2026)": f"""
        SELECT tipo_emenda,
               COUNT(*) AS linhas,
               ROUND(SUM(valor_pago + valor_resto_pagar_pagos) / 1e9, 2) AS pago_bi
        FROM {TABELA}
        WHERE ano_emenda BETWEEN 2019 AND 2026
        GROUP BY tipo_emenda
        ORDER BY pago_bi DESC
    """,
    "Com x sem município (2019-2026, tipos individuais)": f"""
        SELECT id_municipio_gasto IS NOT NULL AS tem_municipio,
               COUNT(*) AS linhas,
               ROUND(SUM(valor_pago + valor_resto_pagar_pagos) / 1e9, 2) AS pago_bi
        FROM {TABELA}
        WHERE ano_emenda BETWEEN 2019 AND 2026
          AND LOWER(tipo_emenda) LIKE '%individual%'
        GROUP BY tem_municipio
    """,
    "Exemplos de localidade sem município": f"""
        SELECT localidade, COUNT(*) AS linhas
        FROM {TABELA}
        WHERE ano_emenda BETWEEN 2019 AND 2026
          AND LOWER(tipo_emenda) LIKE '%individual%'
          AND id_municipio_gasto IS NULL
        GROUP BY localidade
        ORDER BY linhas DESC
        LIMIT 10
    """,
}

for titulo, sql in consultas.items():
    print(f"\n== {titulo}")
    print(bd.read_sql(sql, billing_project_id=projeto).to_string(index=False))
