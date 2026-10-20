# PRD — Emenda vira voto?

**Projeto:** participação no #DataGlowUp (Heitor Sasaki), edição dados do Senado
**Autor:** Luis
**Versão:** 1.0 — 19/10/2026
**Publicação-alvo:** sábado, 24/10/2026 (véspera do 2º turno)
**Repositório:** `emenda-vira-voto` (público, GitHub)

---

## 1. Contexto

O Data Glow Up pede uma análise que **conte uma história** com três bases da Base dos Dados (Senado legislativo, Senado administrativo e Emendas Parlamentares do Portal da Transparência), publicada no LinkedIn com #DataGlowUp. Dashboard com mil filtros não vale. Fonte e conta precisam estar explícitas, porque é dado político e vai ter gente contestando.

O momento é favorável: o 1º turno (04/10/2026) já definiu o Senado. Dos 32 senadores que tentaram a reeleição, 14 se reelegeram e 18 perderam. A imprensa já comparou o **volume médio** de emendas entre reeleitos e derrotados por senador (e encontrou praticamente empate). Ninguém, até onde se sabe, desceu ao **nível do município**.

## 2. A história (hipótese central)

> **Pergunta:** nos municípios que mais receberam emendas de um senador, ele teve mais votos em 2026?

Para cada um dos 32 senadores que tentaram a reeleição, comparamos, **dentro do próprio estado**, município a município:

- **X** = emendas individuais do senador destinadas ao município (2019–2026), em R$ por habitante;
- **Y** = percentual de votos válidos do senador naquele município em 04/10/2026.

**Por que funciona em qualquer resultado:**

| Se o dado mostrar… | Manchete |
|---|---|
| Relação forte | "Onde a emenda chegou, o voto veio: o mapa de 32 senadores" |
| Relação fraca/nula | "Emenda não comprou voto: R$ X bilhões e nenhuma correlação" |
| Misto | "Para uns funcionou, para outros não: quem mais 'converteu' emenda em voto" |

A comparação **dentro do estado** evita comparar Amapá com São Paulo e é o diferencial em relação ao que já foi publicado.

**Correlação não é causalidade.** Isso aparece no post, na página e na metodologia (ver seção 7).

## 3. Objetivos e métricas de sucesso

| Objetivo | Critério de sucesso |
|---|---|
| Publicar a história até 24/10 | Post no LinkedIn com #DataGlowUp e marcação do Heitor |
| Credibilidade | Toda cifra do post rastreável a uma query no repositório |
| Portfólio técnico | Pipeline medalhão no Databricks + automação n8n em Docker documentados no README |
| Automação | Pelo menos 1 execução real do boletim semanal entregue no Telegram |

## 4. Público

1. **Comunidade de dados no LinkedIn** (recrutadores, participantes do desafio): querem ver stack, método e clareza.
2. **Público geral/eleitor:** quer o mapa e "meu senador mandou quanto para minha cidade?".
3. **Céticos/críticos:** querem ver a fonte e refazer a conta.

## 5. Escopo (MoSCoW)

### Must — até 24/10
- **M1.** Pipeline Databricks (catálogo novo `data_glow_up`) com bronze/silver/gold para emendas, votação TSE e população.
- **M2.** Análise central: correlação emenda per capita × % de votos, por senador, dentro do estado (32 senadores).
- **M3.** Página web estática (GitHub Pages) com a história em rolagem: 1 mapa + 2–3 gráficos + metodologia.
- **M4.** Post no LinkedIn com carrossel (4–6 imagens exportadas da página).
- **M5.** `METODOLOGIA.md` no repositório com fontes, filtros, fórmulas e limitações.

### Should — se o tempo permitir antes de 24/10
- **S1.** Automação "Radar do Senado" (seção 9): boletim semanal via n8n em Docker → Telegram.
- **S2.** Recorte "busque seu município/estado" na página (um seletor, não um painel de filtros).

### Could — depois da publicação
- **C1.** Dashboard AI/BI no Databricks como apêndice exploratório.
- **C2.** Alerta de cota fora do padrão como fluxo separado, em tempo real.
- **C3.** Repetir a análise para deputados federais.

### Won't (nesta versão)
- Perfil automático no X postando votos.
- Qualquer inferência causal ou juízo sobre conduta de parlamentares.

## 6. Fontes de dados

| # | Fonte | Uso | Acesso |
|---|---|---|---|
| F1 | **Emendas Parlamentares** — CGU/Portal da Transparência (Base dos Dados), 2013–2026 | X: valores por autor e localidade | BigQuery via `basedosdados` |
| F2 | **Senado Legislativo** (Base dos Dados), até 02/10/2026 | Lista de senadores, partido, UF, código | BigQuery |
| F3 | **Senado Administrativo** (Base dos Dados), até 31/08/2026 | Cota (CEAPS) — contexto e automação | BigQuery |
| F4 | **TSE — Portal de Dados Abertos**, resultados 2026 (votação por candidato e município) | Y: votos por município | Download CSV (fonte externa) |
| F5 | **IBGE** — população municipal (estimativa/Censo mais recente) | Denominador per capita | Base dos Dados (diretórios/população) |
| F6 | **Diretório de municípios** Base dos Dados | De-para código TSE ↔ código IBGE | BigQuery |
| F7 | **APIs de dados abertos do Senado** (legislativo e administrativo) | Automação semanal (dados mais frescos que a Base dos Dados) | HTTP, direto do n8n |

> Nomes exatos de tabelas e colunas: confirmar na Fase 0 e registrar em `docs/fontes.md`.

## 7. Metodologia e regras de cálculo

**Universo de senadores:** os 32 que concorreram à reeleição em 2026 (lista conferida com resultado oficial do TSE).

**Emendas (X):**
- Somente **emendas individuais** cujo autor é o senador (excluir bancada, comissão e relator; RP9 não é atribuível por autor nesta base).
- Período: **ano da emenda 2020–2026** — emendas apresentadas durante o mandato que se encerrava (as de ano 2019 foram apresentadas no fim de 2018, no mandato anterior). Pagamentos até 09/2026. *(Revisado em 20/10/2026; antes: 2019–2026.)*
- Valor: **pago** (incluindo restos a pagar pagos). Valor empenhado como análise de sensibilidade.
- Localidade: apenas emendas com **município identificado**. Reportar o % do total que ficou sem município (estadual/nacional) — esse número vai no post. *(20/10/2026: município atribuído pelo arquivo "por favorecido" do Portal da Transparência, só quando o favorecido é o próprio ente municipal — ver `METODOLOGIA.md`.)*
- Valores nominais (sem correção) na v1; IPCA como Could.

**Votos (Y):** votos nominais do senador ÷ votos válidos para senador no município (lembrando que em 2026 cada eleitor votou em 2 senadores — usar a definição do TSE e documentar).

**Métrica por senador:** correlação de Spearman entre X per capita e Y, ponderada por eleitorado como sensibilidade. Spearman porque emenda per capita tem cauda longa.

**Regras de leitura:**
- Mínimo de 15 municípios com emenda para o senador entrar no ranking. Roraima (15 municípios) fica no limite: registrado como limitação de estado pequeno.
- **Cobertura mínima de 20%:** o R$ atribuível a municípios da própria UF precisa ser ≥ 20% do R$ em emendas individuais do senador. Quem fica abaixo sai do ranking e aparece na página como perfil de destinação diferente (ex.: governo estadual), em linguagem neutra. *(20/10/2026)*
- **DF fora do ranking:** com um único município, a comparação dentro do estado não se aplica. *(20/10/2026)*
- Exibir sempre n, ρ e intervalo/valor-p; não destacar ρ isolado de amostra pequena.
- Linguagem descritiva: "municípios que receberam mais tiveram/não tiveram mais votos". Nunca "comprou", "pagou por", sem aspas de manchete testada.

**Limitações declaradas:** causalidade reversa (emenda vai para base já fiel), prefeitos aliados, incumbência, eleitorado ≠ população, emendas sem município.

Toda tabela gold tem uma query de reprodução versionada em `sql/gold/`.

## 8. Arquitetura

```
 BigQuery (Base dos Dados)      TSE CSV        IBGE
        │  basedosdados (Python)    │  download    │
        ▼                           ▼              ▼
 ┌──────────────── Databricks Free Edition ────────────────┐
 │ catálogo data_glow_up                                   │
 │  bronze  ─►  silver  ─►  gold                           │
 │  (cru)      (limpo,     (emenda_mun_senador,            │
 │             de-para)     voto_mun_senador,              │
 │                          correlacao_senador)            │
 └──────────────┬──────────────────────────────────────────┘
                │ export JSON/GeoJSON
                ▼
   site/ (GitHub Pages: mapa + gráficos + metodologia)
                │
                ▼
      Carrossel LinkedIn #DataGlowUp

 ┌─────── Docker (máquina pessoal) ───────┐
 │ n8n — Radar do Senado (semanal)        │
 │ APIs Senado ► regras ► LLM ► Telegram  │
 └────────────────────────────────────────┘
```

**Decisões:**
- **Ingestão:** script Python (`ingest/`) usando `basedosdados` + service account GCP, gravando Parquet e subindo para um Volume do Unity Catalog. Rodar dentro do Databricks se a Free Edition permitir saída para o BigQuery; senão, localmente (venv ou container) e upload pelo Databricks CLI. Decisão na Fase 0.
- **Transformação:** notebooks/SQL no Databricks, versionados no repo (Databricks Asset Bundle ou pasta `notebooks/` sincronizada).
- **Visualização pública:** página estática (HTML + Leaflet/MapLibre + biblioteca de gráficos via CDN). Sem backend.
- **Malha municipal:** GeoJSON simplificado do IBGE (fonte declarada).
- **Desenvolvimento:** VS Code + Claude Code, regras do projeto no `CLAUDE.md`.

## 9. Automação — Radar do Senado (Should)

**Gatilho:** toda segunda-feira, 8h (cron no n8n, container Docker local).

**Fluxo:**
1. Buscar votações nominais da semana anterior na API legislativa do Senado.
2. Buscar despesas novas da CEAPS na API administrativa.
3. Regra de cota fora do padrão: despesa acima de **Q3 + 3×IQR do histórico do próprio senador no mesmo tipo de despesa** (últimos 24 meses, mínimo de 12 lançamentos).
4. LLM gera o boletim **somente a partir do JSON** dos passos 1–3 (prompt proíbe adjetivos, opinião e informação externa; cada número com link da fonte).
5. **Revisão humana:** rascunho chega no Telegram privado do Luis com botões Aprovar/Descartar (n8n "send and wait for response").
6. Se aprovado: envia para canal público no Telegram e/ou e-mail.

**Limitações conhecidas:** roda só com a máquina ligada; semanas sem votação geram boletim curto ("sem votações nominais").

## 10. Estrutura do repositório

```
emenda-vira-voto/
├── PRD.md
├── README.md            # história + como reproduzir
├── METODOLOGIA.md       # fontes, filtros, fórmulas, limitações
├── CLAUDE.md            # regras para o agente
├── ingest/              # extração BigQuery/TSE/IBGE
├── notebooks/           # bronze, silver, gold
├── sql/gold/            # queries de reprodução de cada número
├── site/                # página estática (GitHub Pages)
├── n8n/                 # workflow exportado (.json) + docker-compose.yml
├── docs/fontes.md
└── assets/carrossel/
```

## 11. Cronograma (5 noites × 1–2 h)

| Dia | Entrega | Go/No-go |
|---|---|---|
| **Seg 19/10** | Repo + CLAUDE.md; GCP/BD funcionando; confirmar tabelas; **checar se o arquivo TSE 2026 por município já está publicado** | Se TSE 2026 indisponível → plano B (seção 13) |
| **Ter 20/10** | Bronze + silver: emendas (32 senadores), votos TSE, população, de-para | — |
| **Qua 21/10** | Gold + análise: ρ por senador, ranking, 3 achados principais | Escolher a manchete |
| **Qui 22/10** | Página web (mapa + 2–3 gráficos + metodologia) publicada no GitHub Pages | — |
| **Sex 23/10** | Carrossel + texto do post; n8n se sobrar tempo (Should) | Automação vira "próximo passo" se não couber |
| **Sáb 24/10** | Revisão de números, post no LinkedIn | — |

## 12. Critérios de aceite

- [ ] Cada número do post tem query em `sql/gold/` e aparece igual na página.
- [ ] Página explica em até 3 parágrafos o que foi medido e o que **não** foi.
- [ ] % de emendas sem município identificado declarado.
- [ ] Os 32 senadores listados com n, ρ e resultado eleitoral, sem adjetivos.
- [ ] README permite a terceiros reproduzir com conta GCP própria.
- [ ] Post com #DataGlowUp, marcação do Heitor e link para página + repo.

## 13. Riscos e mitigação

| Risco | Prob. | Impacto | Mitigação |
|---|---|---|---|
| Resultado TSE 2026 por município ainda não publicado em dados abertos | Média | Alto | Plano B: mapa per capita "quem mandou emenda para onde" + concentração por senador (vira a história central) |
| Free Edition sem saída para BigQuery ou com cota de compute | Média | Médio | Ingestão local + upload para Volume |
| Grande parte das emendas sem município identificado | Média | Médio | Declarar %; análise apenas no subconjunto e sensibilidade |
| Tempo (5–10 h no total) | Alta | Alto | MoSCoW rígido; automação é Should; Claude Code para acelerar código repetitivo |
| Contestação política | Alta | Médio | Metodologia aberta, linguagem descritiva, mesmo tratamento para todos os partidos |
| LLM alucinar no boletim | Média | Alto | Entrada só JSON, revisão humana antes de publicar |

## 14. Decisões em aberto

1. Qual LLM/chave usar no n8n (Claude API ou outro)?
2. Canal público no Telegram ou apenas e-mail para o boletim?
3. Correção monetária (IPCA) entra na v1 ou fica como Could?
4. Título final do projeto ("Emenda vira voto?" é provisório).
