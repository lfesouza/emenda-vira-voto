# CLAUDE.md — Emenda vira voto?

Leia o `PRD.md` antes de qualquer tarefa. Ele é a fonte da verdade de escopo, metodologia e cronograma.

## Sobre o projeto
Análise para o desafio #DataGlowUp: emendas parlamentares × votos dos 32 senadores que tentaram a reeleição em 2026, comparados município a município dentro do estado. Publicação no LinkedIn em 24/10/2026. Repositório público.

## Sobre quem desenvolve
- Luis, analista de processos migrando para dados. Forte em Power BI/Excel, SQL intermediário (JOIN, GROUP BY; window functions e CTEs ainda em aprendizado), Python em evolução, n8n experiente.
- Docker: tem rodando na máquina pessoal, pouca experiência em linha de comando. Explique comandos de terminal antes de pedir para rodar.
- Tempo: 1–2 h por noite. Prefira entregas pequenas que terminem na mesma sessão.
- Idioma: português do Brasil em tudo (comentários, commits, docs).

## Princípios de trabalho
1. **Pense antes de codar.** Diga o que vai fazer e quais suposições está assumindo. Se algo do PRD estiver ambíguo, pergunte em vez de escolher em silêncio.
2. **Simplicidade primeiro.** O mínimo de código que resolve. Nada de abstração, configuração ou dependência "para o futuro".
3. **Mudanças cirúrgicas.** Mexa só no que a tarefa pede. Não reformate nem refatore arquivos vizinhos.
4. **Execução guiada por objetivo.** Antes de começar, defina como verificar que deu certo (contagem de linhas, soma que bate com a fonte, página que abre). Verifique antes de dizer que terminou.

## Regras de dados (inegociáveis)
- Todo número que vai para o post ou para a página precisa de uma query em `sql/gold/` que o reproduza.
- Nunca invente nomes de tabelas ou colunas da Base dos Dados ou do TSE: consulte o schema real e registre em `docs/fontes.md`.
- Ao filtrar ou descartar dados, registre quantas linhas e quanto R$ saíram, e por quê, em `METODOLOGIA.md`.
- Linguagem descritiva e neutra. Proibido: "comprou voto", juízo sobre conduta, adjetivos sobre parlamentares. Mesmo tratamento para todos os partidos.
- Correlação não é causalidade: toda saída analítica mostra n e ρ juntos.

## Segurança (repositório público)
- Credenciais (chave GCP, token do Telegram, chave de LLM, token Databricks) só em `.env` ou arquivos listados no `.gitignore`. Nunca em código, notebook ou workflow n8n exportado.
- Antes de cada commit, confira `git status` para não subir chave nem dado bruto pesado.

## Stack
- Ingestão: Python + `basedosdados` (BigQuery), CSV do TSE, IBGE.
- Transformação: Databricks Free Edition, catálogo `data_glow_up`, camadas bronze/silver/gold.
- Visualização pública: `site/` estático (HTML + mapa + gráficos via CDN), GitHub Pages.
- Automação: n8n em Docker local (`n8n/docker-compose.yml`), saída no Telegram com aprovação humana.

## Estrutura
Siga a seção 10 do PRD. Não crie pastas fora dela sem perguntar.

## Fluxo de trabalho
- Uma fase do cronograma (PRD seção 11) por sessão.
- Ao fim de cada sessão: resumo do que foi feito, o que ficou pendente e commit com mensagem clara.
