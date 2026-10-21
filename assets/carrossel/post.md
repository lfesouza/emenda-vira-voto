# Texto do post (LinkedIn)

Números: `sql/gold/01_totais.sql` (R$ 8,74 bi; 53,1%), `02_resumo_cenarios.sql` e `03_robustez.sql` (18 de 29; nenhum negativo significativo; ρ 0,24 / 0,25 / 0,08; 24 de 29). Anexar `emenda-vira-voto.pdf` como documento. Marcar o Heitor Sasaki manualmente no LinkedIn.

---

Emenda vira voto?

Nos municípios que mais receberam emendas de um senador, ele teve mais votos em 2026?

Para responder, cruzei as emendas individuais dos 32 senadores que tentaram a reeleição com o resultado do 1º turno, município a município, dentro de cada estado.

O que os dados mostram:

→ R$ 8,74 bi em emendas individuais desses 32 senadores (emendas de 2020 a 2026). 53,1% foram pagos ao próprio município e entram na comparação. O resto (governo estadual, Banco do Brasil como intermediário, entidades) fica de fora.

→ Em 18 dos 29 senadores analisados, a correlação entre emenda per capita e % de votos no município é positiva e estatisticamente significativa. Em nenhum ela é negativa e significativa.

→ A relação é moderada: ρ de Spearman mediano de 0,24.

→ Ela se mantém quando controlo pelo tamanho do município (0,25). Mas, no teste placebo, trocando a emenda do senador pela dos outros parlamentares, o ρ mediano cai para 0,08. Em 24 dos 29, a emenda do próprio senador acompanha o voto mais do que a dos outros; em alguns, a relação parece ser do perfil do município.

Correlação não é causalidade: a emenda pode ir para onde o senador já tinha voto, e fatores como prefeitos aliados não foram medidos.

Escolha o senador e veja o mapa: https://lfesouza.github.io/emenda-vira-voto/
Código, consultas SQL e metodologia: https://github.com/lfesouza/emenda-vira-voto

Stack: Python + Base dos Dados (BigQuery), Databricks Free Edition (bronze/silver/gold), D3 e GitHub Pages. Cada número do post tem uma consulta em sql/gold/ que o reproduz.

Feito para o desafio #DataGlowUp, do @Heitor Sasaki.

#DataGlowUp #AnaliseDeDados #SQL #Databricks #Eleicoes2026
