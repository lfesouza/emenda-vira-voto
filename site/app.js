// Página "Emenda vira voto?": lê os JSON gerados por ingest/exporta_site.py (uma query de sql/gold/ cada).
const REPO_URL = "https://github.com/lfesouza/emenda-vira-voto";

const fmt = {
  num: (v, casas = 0) => v.toLocaleString("pt-BR", { minimumFractionDigits: casas, maximumFractionDigits: casas }),
  rs: v => "R$ " + v.toLocaleString("pt-BR", { maximumFractionDigits: 0 }),
  rho: v => (v == null ? "—" : v.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })),
  p: v => (v == null ? "—" : v < 0.001 ? "< 0,001" : v.toLocaleString("pt-BR", { maximumFractionDigits: 3 })),
};
const css = nome => getComputedStyle(document.documentElement).getPropertyValue(nome).trim();
const tooltip = document.getElementById("tooltip");

function mostraTooltip(evento, html) {
  tooltip.innerHTML = html;
  tooltip.hidden = false;
  const { innerWidth: w } = window;
  const x = Math.min(evento.clientX + 14, w - tooltip.offsetWidth - 8);
  tooltip.style.left = x + "px";
  tooltip.style.top = evento.clientY + 14 + "px";
}
const escondeTooltip = () => { tooltip.hidden = true; };

Promise.all(
  ["01_totais", "03_robustez", "04_ranking", "05_municipios", "09_casos_concretos", "11_senador_mapa", "08_resumo_2018"].map(n => d3.json(`data/${n}.json`))
).then(([totais, robustez, ranking, municipios, casos, senadorMapa, resumo2018]) => {
  const t = totais[0];
  const r = robustez[0];
  const e = resumo2018[0];
  document.getElementById("e-n2018").textContent = e.senadores;
  document.getElementById("m-2018").textContent =
    `Em ${e.variacao_positivo_p05} de ${e.senadores}, onde chegou mais emenda, o voto cresceu mais entre 2018 e 2026 ` +
    `(ρ > 0, p < 0,05); ${e.variacao_negativo_p05 === 0 ? "nenhum mostra o contrário" : `${e.variacao_negativo_p05} mostram o contrário`}.`;
  document.getElementById("e-2018-voto").textContent =
    `Com o voto de 2018, ${e.voto_2018_positivo_p05} de ${e.senadores} têm relação positiva estatisticamente ` +
    `significativa e ${e.voto_2018_negativo_p05} tem relação negativa significativa. n de ${e.n_minimo} a ` +
    `${fmt.num(e.n_maximo, 0)} municípios por senador.`;
  document.getElementById("t-rs").textContent = `R$ ${fmt.num(t.rs_individual_bi, 2)} bi`;
  document.getElementById("t-pct").textContent = `${fmt.num(t.pct_com_municipio, 1)}%`;
  document.getElementById("t-sig").textContent = `${r.rho_positivo_p05} de ${r.senadores}`;
  document.getElementById("m-sem").textContent = `${fmt.num(t.pct_sem_municipio, 1)}%`;
  document.getElementById("link-repo").href = REPO_URL;

  const porSenador = d3.group(municipios, m => m.id_senador);
  const noRanking = ranking.filter(s => s.no_ranking).sort((a, b) => b.rho - a.rho);

  desenhaRanking(noRanking);
  desenhaRobustez(r);
  desenha2018(e);
  preencheTabela(ranking);
  preencheCasos(casos, senadorMapa[0]);
  montaSeletor(ranking.filter(s => s.sigla_uf !== "DF"), porSenador);

  let largura = window.innerWidth;
  window.addEventListener("resize", () => {
    if (Math.abs(window.innerWidth - largura) < 40) return;
    largura = window.innerWidth;
    desenhaRanking(noRanking);
    desenhaRobustez(r);
    desenha2018(e);
    document.getElementById("sel-senador").dispatchEvent(new Event("change"));
  });
  // Troca de tema do sistema: redesenha com as cores do novo modo
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => {
    desenhaRanking(noRanking);
    desenhaRobustez(r);
    desenha2018(e);
    document.getElementById("sel-senador").dispatchEvent(new Event("change"));
  });
});

// Gráfico 1: ρ do senador × placebo (emenda dos outros), uma linha por senador
function desenhaRanking(dados) {
  const el = document.getElementById("g-ranking");
  el.innerHTML = "";
  const w = el.clientWidth - 16;
  const estreito = w < 520;
  const m = { top: 24, right: 16, bottom: 28, left: estreito ? 150 : 190 };
  const linha = 24;
  const h = m.top + m.bottom + linha * dados.length;
  const x = d3.scaleLinear().domain([-0.7, 0.85]).range([m.left, w - m.right]);
  const y = d3.scaleBand().domain(dados.map(d => d.id_senador)).range([m.top, h - m.bottom]);
  const svg = d3.select(el).append("svg").attr("viewBox", `0 0 ${w} ${h}`);

  svg.append("g").attr("class", "grade")
    .selectAll("line").data(x.ticks(6)).join("line")
    .attr("x1", d => x(d)).attr("x2", d => x(d)).attr("y1", m.top - 8).attr("y2", h - m.bottom);
  svg.append("line").attr("x1", x(0)).attr("x2", x(0)).attr("y1", m.top - 8).attr("y2", h - m.bottom)
    .attr("stroke", css("--eixo")).attr("stroke-width", 1.5);
  svg.append("g").attr("class", "eixo").attr("transform", `translate(0,${h - m.bottom})`)
    .call(d3.axisBottom(x).ticks(6).tickFormat(v => fmt.num(v, 1)).tickSizeOuter(0))
    .call(g => g.select(".domain").remove());
  svg.append("text").attr("x", x(0) + 4).attr("y", m.top - 12).text("ρ").style("fill", css("--tinta-3"));

  const g = svg.append("g").selectAll("g").data(dados).join("g")
    .attr("transform", d => `translate(0,${y(d.id_senador) + y.bandwidth() / 2})`)
    .style("cursor", "pointer");
  g.append("rect").attr("class", "linha-hover").attr("x", 0).attr("width", w)
    .attr("y", -linha / 2).attr("height", linha);
  g.append("text").attr("x", m.left - 10).attr("dy", "0.32em").attr("text-anchor", "end")
    .style("fill", css("--tinta")).style("font-size", estreito ? "11px" : null)
    .text(d => (estreito ? curto(d.nome_parlamentar) : d.nome_parlamentar) + ` (${d.sigla_uf})`);
  g.append("line").attr("x1", d => x(d.rho)).attr("x2", d => x(d.rho_placebo_emenda_outros))
    .attr("stroke", css("--eixo")).attr("stroke-width", 2);
  const ponto = (sel, campo, cor, cheio) => sel.append("circle")
    .attr("cx", d => x(d[campo])).attr("r", 5)
    .attr("fill", d => (cheio(d) ? cor : css("--superficie")))
    .attr("stroke", cor).attr("stroke-width", 2);
  ponto(g, "rho_placebo_emenda_outros", css("--serie-2"), () => true);
  ponto(g, "rho", css("--serie-1"), d => d.p_valor < 0.05);

  g.on("mousemove", (e, d) => mostraTooltip(e,
      `<strong>${d.nome_parlamentar} (${d.sigla_partido}-${d.sigla_uf})</strong>` +
      `<span class="t2">${d.situacao_2026 === "ELEITO" ? "Reeleito" : "Não reeleito"} · ${d.n} municípios, ${d.n_com_emenda} com emenda</span><br>` +
      `ρ = ${fmt.rho(d.rho)} (p ${fmt.p(d.p_valor).startsWith("<") ? "" : "= "}${fmt.p(d.p_valor)})<br>` +
      `Placebo (emenda dos outros): ρ = ${fmt.rho(d.rho_placebo_emenda_outros)}`))
    .on("mouseleave", escondeTooltip)
    .on("click", (e, d) => {
      const sel = document.getElementById("sel-senador");
      sel.value = d.id_senador;
      sel.dispatchEvent(new Event("change"));
      sel.scrollIntoView({ behavior: "smooth", block: "center" });
    });
}

const curto = nome => {
  const p = nome.split(" ");
  return p.length > 2 ? `${p[0]} ${p[p.length - 1]}` : nome;
};

// Gráfico 3: ρ mediano por teste
function desenhaRobustez(r) {
  const dados = [
    { teste: "Original", curto: "Original", v: r.rho_mediano, placebo: false },
    { teste: "Controlando pela população", curto: "Controle: população", v: r.parcial_pop_mediano, placebo: false },
    { teste: "Ponderado pelos votos válidos", curto: "Ponderado: votos", v: r.ponderado_votos_mediano, placebo: false },
    { teste: "Placebo: emenda dos outros parlamentares", curto: "Placebo: emenda outros", v: r.placebo_emenda_outros_mediano, placebo: true },
    { teste: "Placebo: voto dos outros candidatos*", curto: "Placebo: voto outros*", v: r.placebo_voto_outros_mediano, placebo: true },
  ];
  desenhaBarras("g-robustez", dados, [-0.2, 0.3],
    "* referência fraca: os % de um município somam 200%, o que puxa o ρ para baixo");
}

function desenha2018(e) {
  const dados = [
    { teste: "Emenda × voto 2018", curto: "Voto 2018", v: e.rho_voto_2018_mediano, placebo: false },
    { teste: "Emenda × variação 2018→2026", curto: "Variação 2018→2026", v: e.rho_variacao_mediano, placebo: false },
    { teste: "Emenda × voto 2026 (mesmos senadores)", curto: "Voto 2026", v: e.rho_2026_mediano_mesmos, placebo: false },
  ];
  desenhaBarras("g-2018", dados, [0, 0.3], null);
}

// Barras horizontais de ρ mediano; nota opcional no rodapé
function desenhaBarras(id, dados, dominio, nota) {
  const el = document.getElementById(id);
  el.innerHTML = "";
  const w = el.clientWidth - 16;
  const estreito = w < 520;
  const m = { top: 8, right: 48, bottom: 40, left: estreito ? 130 : 260 };
  const barra = 18, passo = 34;
  const h = m.top + m.bottom + passo * dados.length;
  const x = d3.scaleLinear().domain(dominio).range([m.left, w - m.right]);
  const svg = d3.select(el).append("svg").attr("viewBox", `0 0 ${w} ${h}`);
  svg.append("g").attr("class", "grade").selectAll("line").data(x.ticks(5)).join("line")
    .attr("x1", d => x(d)).attr("x2", d => x(d)).attr("y1", m.top).attr("y2", h - m.bottom);
  svg.append("g").attr("class", "eixo").attr("transform", `translate(0,${h - m.bottom})`)
    .call(d3.axisBottom(x).ticks(5).tickFormat(v => fmt.num(v, 1)).tickSizeOuter(0))
    .call(g => g.select(".domain").remove());
  const g = svg.append("g").selectAll("g").data(dados).join("g")
    .attr("transform", (d, i) => `translate(0,${m.top + i * passo + passo / 2})`);
  g.append("text").attr("x", m.left - 10).attr("dy", "0.32em").attr("text-anchor", "end")
    .style("fill", css("--tinta")).text(d => (estreito ? d.curto : d.teste))
    .call(sel => estreito && sel.style("font-size", "11px"));
  // Barra com ponta arredondada só na extremidade do valor
  g.append("path").attr("fill", d => css(d.placebo ? "--serie-2" : "--serie-1"))
    .attr("d", d => barraArredondada(x(0), x(d.v), -barra / 2, barra, 4));
  g.append("text").attr("x", d => x(d.v) + (d.v >= 0 ? 6 : -6)).attr("dy", "0.32em")
    .attr("text-anchor", d => (d.v >= 0 ? "start" : "end")).style("fill", css("--tinta"))
    .text(d => fmt.rho(d.v));
  svg.append("line").attr("x1", x(0)).attr("x2", x(0)).attr("y1", m.top).attr("y2", h - m.bottom)
    .attr("stroke", css("--eixo")).attr("stroke-width", 1.5);
  if (nota) svg.append("text").attr("x", m.left).attr("y", h - 4).style("font-size", "11px").text(nota);
}

function barraArredondada(x0, x1, y, h, raio) {
  const r = Math.min(raio, Math.abs(x1 - x0), h / 2);
  if (x1 >= x0) {
    return `M${x0},${y}H${x1 - r}Q${x1},${y} ${x1},${y + r}V${y + h - r}Q${x1},${y + h} ${x1 - r},${y + h}H${x0}Z`;
  }
  return `M${x0},${y}H${x1 + r}Q${x1},${y} ${x1},${y + r}V${y + h - r}Q${x1},${y + h} ${x1 + r},${y + h}H${x0}Z`;
}

// Seletor + mapa + dispersão do senador escolhido
const malhas = new Map();
function montaSeletor(senadores, porSenador) {
  const sel = document.getElementById("sel-senador");
  const ordem = [...senadores].sort((a, b) => a.sigla_uf.localeCompare(b.sigla_uf) || a.nome_parlamentar.localeCompare(b.nome_parlamentar));
  sel.innerHTML = ordem.map(s =>
    `<option value="${s.id_senador}">${s.sigla_uf} — ${s.nome_parlamentar}${s.no_ranking ? "" : " (fora do ranking)"}</option>`).join("");
  sel.addEventListener("change", async () => {
    const s = senadores.find(x => x.id_senador === sel.value);
    if (!malhas.has(s.sigla_uf)) malhas.set(s.sigla_uf, await d3.json(`data/geo/${s.sigla_uf}.json`));
    const dados = porSenador.get(s.id_senador);
    resumo(s);
    desenhaMapaDispersao(s, dados, malhas.get(s.sigla_uf));
  });
  sel.dispatchEvent(new Event("change"));
}

// Casos concretos (sql/gold/09) e o senador escolhido para o carrossel (sql/gold/11)
function preencheCasos(casos, sm) {
  document.getElementById("c-carrossel").textContent =
    `O carrossel do LinkedIn mostra só ${sm.nome_parlamentar}, escolhido pela regra: maior ρ entre os senadores cujo ` +
    `ρ do placebo (emenda dos outros) fica pelo menos 0,2 abaixo do próprio ρ (${fmt.rho(sm.rho_placebo_emenda_outros)} contra ${fmt.rho(sm.rho)}).`;
  document.getElementById("casos").innerHTML = casos.map(d => `
    <div class="tile">
      <h3>${d.nome_parlamentar} (${d.sigla_uf})</h3>
      <span class="tile-rotulo">ρ = ${fmt.rho(d.rho)} · n = ${d.n} · p ${fmt.p(d.p_valor).startsWith("<") ? "" : "= "}${fmt.p(d.p_valor)}</span>
      <p class="caso-mun"><strong>${d.municipio}</strong> · ${fmt.num(d.populacao)} hab.</p>
      <span class="tile-valor">R$ ${fmt.num(d.rs_por_habitante, 2)}</span><span class="tile-rotulo">por habitante</span>
      <span class="tile-valor">${fmt.num(d.pct_votos_2026, 1)}%</span><span class="tile-rotulo">dos votos válidos</span>
      ${d.rho - d.rho_placebo_emenda_outros < 0.2 ? `<p class="nota caso-obs">No caso dele, a emenda dos outros parlamentares
        acompanha o voto quase na mesma medida (ρ ${fmt.rho(d.rho_placebo_emenda_outros)} contra ${fmt.rho(d.rho)}).</p>` : ""}
    </div>`).join("");
}

function resumo(s) {
  const el = document.getElementById("resumo-senador");
  const situacao = s.situacao_2026 === "ELEITO" ? "reeleito" : "não reeleito";
  let texto = `${s.nome_parlamentar} (${s.sigla_partido}-${s.sigla_uf}), ${situacao}. ` +
    `R$ ${fmt.num(s.rs_municipal_uf_mi, 1)} milhões pagos a ${s.n_com_emenda} dos ${s.n} municípios do estado. ` +
    `ρ = ${fmt.rho(s.rho)} (p ${fmt.p(s.p_valor).startsWith("<") ? "" : "= "}${fmt.p(s.p_valor)}); ` +
    `placebo = ${fmt.rho(s.rho_placebo_emenda_outros)}.`;
  if (!s.no_ranking) texto += ` Fora do ranking: ${s.motivo_fora}.`;
  el.textContent = texto;
}

function desenhaMapaDispersao(s, dados, geo) {
  const porMun = new Map(dados.map(d => [d.id_municipio, d]));
  const comEmenda = dados.filter(d => d.rs_por_habitante > 0).map(d => d.rs_por_habitante);
  const cores = [1, 2, 3, 4, 5].map(i => css(`--seq-${i}`));
  const escala = d3.scaleQuantile().domain(comEmenda).range(cores);
  const cor = d => (d && d.rs_por_habitante > 0 ? escala(d.rs_por_habitante) : css("--neutro"));

  const tip = d => `<strong>${d.municipio}</strong>` +
    `${d.rs_principal > 0 ? `${fmt.rs(d.rs_principal)} · ${fmt.rs(d.rs_por_habitante)} por habitante` : "Sem emenda do senador"}<br>` +
    `<span class="t2">${fmt.num(d.pct_votos, 1)}% dos votos válidos · ${fmt.num(d.populacao)} hab.</span>`;

  // Mapa
  const elM = document.getElementById("g-mapa");
  elM.innerHTML = "";
  const w = elM.clientWidth - 16, h = Math.round(w * 0.9);
  // Projeção plana: a malha do IBGE vem com polígonos no sentido inverso ao esperado pelas projeções esféricas do D3
  const proj = d3.geoIdentity().reflectY(true).fitSize([w, h], geo);
  const svgM = d3.select(elM).append("svg").attr("viewBox", `0 0 ${w} ${h}`);
  const caminhos = svgM.append("g").selectAll("path").data(geo.features).join("path")
    .attr("d", d3.geoPath(proj))
    .attr("fill", f => cor(porMun.get(f.properties.codarea)))
    .attr("stroke", css("--superficie")).attr("stroke-width", 0.5)
    .on("mousemove", (e, f) => { const d = porMun.get(f.properties.codarea); if (d) { destaca(d.id_municipio); mostraTooltip(e, tip(d)); } })
    .on("mouseleave", () => { destaca(null); escondeTooltip(); });

  // Legenda do mapa (faixas de R$ por habitante)
  const limites = [d3.min(comEmenda), ...escala.quantiles(), d3.max(comEmenda)];
  document.getElementById("legenda-mapa").innerHTML =
    `<span><span class="amostra" style="background:${css("--neutro")}"></span>sem emenda</span>` +
    cores.map((c, i) => `<span><span class="amostra" style="background:${c}"></span>` +
      `${fmt.rs(limites[i])}–${fmt.rs(limites[i + 1])}</span>`).join("");

  // Dispersão
  const elD = document.getElementById("g-dispersao");
  elD.innerHTML = "";
  const m = { top: 12, right: 12, bottom: 40, left: 44 };
  const hD = h;
  const x = d3.scaleSqrt().domain([0, d3.max(dados, d => d.rs_por_habitante) || 1]).nice().range([m.left, w - m.right]);
  const y = d3.scaleLinear().domain([0, d3.max(dados, d => d.pct_votos)]).nice().range([hD - m.bottom, m.top]);
  const svgD = d3.select(elD).append("svg").attr("viewBox", `0 0 ${w} ${hD}`);
  svgD.append("g").attr("class", "grade").selectAll("line").data(y.ticks(5)).join("line")
    .attr("x1", m.left).attr("x2", w - m.right).attr("y1", d => y(d)).attr("y2", d => y(d));
  svgD.append("g").attr("class", "eixo").attr("transform", `translate(0,${hD - m.bottom})`)
    .call(d3.axisBottom(x).ticks(4).tickFormat(v => fmt.num(v)).tickSizeOuter(0));
  svgD.append("g").attr("class", "eixo").attr("transform", `translate(${m.left},0)`)
    .call(d3.axisLeft(y).ticks(5).tickFormat(v => v + "%").tickSizeOuter(0))
    .call(g => g.select(".domain").remove());
  svgD.append("text").attr("x", w - m.right).attr("y", hD - 6).attr("text-anchor", "end")
    .style("font-size", "11px").text("R$ por habitante");
  const pontos = svgD.append("g").selectAll("circle").data(dados).join("circle")
    .attr("cx", d => x(d.rs_por_habitante)).attr("cy", d => y(d.pct_votos)).attr("r", 4)
    .attr("fill", css("--serie-1")).attr("fill-opacity", 0.75)
    .attr("stroke", css("--superficie")).attr("stroke-width", 1);
  // Camada de vizinho mais próximo: não precisa acertar o ponto exato
  const delaunay = d3.Delaunay.from(dados, d => x(d.rs_por_habitante), d => y(d.pct_votos));
  svgD.append("rect").attr("x", m.left).attr("y", m.top).attr("width", w - m.left - m.right)
    .attr("height", hD - m.top - m.bottom).attr("fill", "transparent")
    .on("mousemove", e => {
      const [px, py] = d3.pointer(e);
      const d = dados[delaunay.find(px, py)];
      destaca(d.id_municipio);
      mostraTooltip(e, tip(d));
    })
    .on("mouseleave", () => { destaca(null); escondeTooltip(); });

  // Destaque ligado entre mapa e dispersão
  function destaca(id) {
    caminhos.attr("stroke", f => (f.properties.codarea === id ? css("--tinta") : css("--superficie")))
      .attr("stroke-width", f => (f.properties.codarea === id ? 2 : 0.5));
    caminhos.filter(f => f.properties.codarea === id).raise();
    pontos.attr("r", d => (d.id_municipio === id ? 7 : 4))
      .attr("stroke", d => (d.id_municipio === id ? css("--tinta") : css("--superficie")))
      .attr("stroke-width", d => (d.id_municipio === id ? 2 : 1));
    pontos.filter(d => d.id_municipio === id).raise();
  }
}

// Tabela com os 32
function preencheTabela(ranking) {
  const linhas = [...ranking].sort((a, b) => (b.no_ranking - a.no_ranking) || ((b.rho ?? -9) - (a.rho ?? -9)));
  document.querySelector("#tabela tbody").innerHTML = linhas.map(s => `
    <tr class="${s.no_ranking ? "" : "fora"}">
      <td>${s.sigla_uf}</td><td>${s.nome_parlamentar}</td><td>${s.sigla_partido}</td>
      <td>${s.situacao_2026 === "ELEITO" ? "Reeleito" : "Não reeleito"}</td>
      <td class="num">${fmt.num(s.rs_municipal_uf_mi, 1)}</td><td class="num">${fmt.num(s.cobertura_pct, 1)}%</td>
      <td class="num">${s.n}</td><td class="num">${s.n_com_emenda}</td>
      <td class="num">${fmt.rho(s.rho)}</td><td class="num">${fmt.p(s.p_valor)}</td>
      <td class="num">${fmt.rho(s.rho_parcial_pop)}</td><td class="num">${fmt.rho(s.rho_placebo_emenda_outros)}</td>
      <td>${s.motivo_fora ? "Fora do ranking: " + s.motivo_fora : ""}</td>
    </tr>`).join("");
}
