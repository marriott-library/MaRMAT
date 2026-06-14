/* Top 10 Most Frequent Terms — vertical bar chart colored by dominant category.
   data: [{term, count, category}]. Renders a legend into legendSelector. */

function renderTopTermsBar(selector, legendSelector, data, colors) {
  const container = document.querySelector(selector);
  container.innerHTML = "";
  const legend = legendSelector ? document.querySelector(legendSelector) : null;
  if (legend) legend.innerHTML = "";

  if (!data || !data.length) {
    container.innerHTML = '<div class="chart-empty">No term data</div>';
    return;
  }

  const margin = { top: 10, right: 16, bottom: 96, left: 44 };
  const width = container.clientWidth || 460;
  const height = 320;
  const innerW = width - margin.left - margin.right;
  const innerH = height - margin.top - margin.bottom;

  const svg = d3.select(container).append("svg")
    .attr("class", "chart-svg")
    .attr("viewBox", `0 0 ${width} ${height}`);
  const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

  const x = d3.scaleBand().domain(data.map((d) => d.term)).range([0, innerW]).padding(0.2);
  const y = d3.scaleLinear().domain([0, d3.max(data, (d) => d.count)]).nice().range([innerH, 0]);

  g.append("g").attr("class", "axis").call(d3.axisLeft(y).ticks(5).tickSizeOuter(0));

  const xAxis = g.append("g").attr("class", "axis")
    .attr("transform", `translate(0,${innerH})`)
    .call(d3.axisBottom(x).tickSizeOuter(0));
  xAxis.selectAll("text")
    .attr("transform", "rotate(-45)")
    .style("text-anchor", "end")
    .attr("dx", "-0.5em").attr("dy", "0.25em");

  const colorFor = (d) => (colors && colors[d.category]) || "#CC0000";
  const tip = ensureTooltip();

  g.selectAll("rect").data(data).enter().append("rect")
    .attr("x", (d) => x(d.term))
    .attr("y", (d) => y(d.count))
    .attr("width", x.bandwidth())
    .attr("height", (d) => innerH - y(d.count))
    .attr("fill", colorFor)
    .on("mousemove", (event, d) =>
      showTooltip(tip, event, `${d.term} (${d.category}): ${d.count.toLocaleString()}`))
    .on("mouseout", () => hideTooltip(tip));

  g.selectAll(".bar-label").data(data).enter().append("text")
    .attr("class", "bar-label")
    .attr("x", (d) => x(d.term) + x.bandwidth() / 2)
    .attr("y", (d) => y(d.count) - 4)
    .attr("text-anchor", "middle")
    .text((d) => d.count.toLocaleString());

  // Legend: distinct categories present in the top terms.
  if (legend) {
    const seen = [];
    data.forEach((d) => { if (!seen.includes(d.category)) seen.push(d.category); });
    legend.innerHTML = seen.map((cat) =>
      `<span class="legend__item"><span class="legend__swatch" style="background:${(colors && colors[cat]) || "#CC0000"}"></span>${MaRMAT.esc(cat)}</span>`
    ).join("");
  }
}
