/* Metadata Column Hit Distribution — pie/donut chart.
   data: [{column, count}]. Slice labels (pct + count) shown for slices >= 4%. */

function renderColumnPie(selector, legendSelector, data) {
  const container = document.querySelector(selector);
  container.innerHTML = "";
  const legend = legendSelector ? document.querySelector(legendSelector) : null;
  if (legend) legend.innerHTML = "";

  if (!data || !data.length) {
    container.innerHTML = '<div class="chart-empty">No column data</div>';
    return;
  }

  const width = container.clientWidth || 460;
  const height = 320;
  const radius = Math.min(width, height) / 2 - 12;
  const total = d3.sum(data, (d) => d.count);

  // Palette for columns (distinct from the category palette).
  const palette = ["#CC0000", "#2B6CB0", "#2F855A", "#B7791F", "#6B46C1",
    "#C05621", "#0987A0", "#97266D", "#4A5568", "#1A365D"];
  const color = (i) => palette[i % palette.length];

  const svg = d3.select(container).append("svg")
    .attr("class", "chart-svg")
    .attr("viewBox", `0 0 ${width} ${height}`);
  const g = svg.append("g").attr("transform", `translate(${width / 2},${height / 2})`);

  const pie = d3.pie().sort(null).value((d) => d.count);
  const arc = d3.arc().innerRadius(radius * 0.5).outerRadius(radius);
  const labelArc = d3.arc().innerRadius(radius * 0.75).outerRadius(radius * 0.75);
  const arcs = pie(data);
  const tip = ensureTooltip();

  g.selectAll("path").data(arcs).enter().append("path")
    .attr("d", arc)
    .attr("fill", (d, i) => color(i))
    .attr("stroke", "#fff")
    .attr("stroke-width", 1.5)
    .on("mousemove", (event, d) => {
      const pct = ((d.data.count / total) * 100).toFixed(1);
      showTooltip(tip, event, `${d.data.column}: ${d.data.count.toLocaleString()} (${pct}%)`);
    })
    .on("mouseout", () => hideTooltip(tip));

  g.selectAll(".slice-label").data(arcs).enter().append("text")
    .attr("class", "bar-label")
    .attr("transform", (d) => `translate(${labelArc.centroid(d)})`)
    .attr("text-anchor", "middle")
    .attr("fill", "#fff")
    .style("font-weight", "600")
    .each(function (d) {
      const pct = (d.data.count / total) * 100;
      if (pct < 4) return;
      const sel = d3.select(this);
      sel.append("tspan").attr("x", 0).attr("dy", "-0.1em").text(`${pct.toFixed(1)}%`);
      sel.append("tspan").attr("x", 0).attr("dy", "1.1em").text(`(${d.data.count.toLocaleString()})`);
    });

  if (legend) {
    legend.innerHTML = data.map((d, i) =>
      `<span class="legend__item"><span class="legend__swatch" style="background:${color(i)}"></span>${MaRMAT.esc(d.column)}</span>`
    ).join("");
  }
}
