/* Category Distribution — horizontal bar chart (D3 v7).
   data: [{category, count}] (already sorted descending by the backend). */

function renderCategoryBar(selector, data, colors) {
  const container = document.querySelector(selector);
  container.innerHTML = "";
  if (!data || !data.length) {
    container.innerHTML = '<div class="chart-empty">No category data</div>';
    return;
  }

  // Ascending so the largest bar sits on top.
  const rows = data.slice().sort((a, b) => a.count - b.count);

  const margin = { top: 10, right: 48, bottom: 36, left: 140 };
  const width = container.clientWidth || 460;
  const height = 320;
  const innerW = width - margin.left - margin.right;
  const innerH = height - margin.top - margin.bottom;

  const svg = d3.select(container).append("svg")
    .attr("class", "chart-svg")
    .attr("viewBox", `0 0 ${width} ${height}`);
  const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

  const x = d3.scaleLinear().domain([0, d3.max(rows, (d) => d.count)]).nice().range([0, innerW]);
  const y = d3.scaleBand().domain(rows.map((d) => d.category)).range([innerH, 0]).padding(0.18);

  g.append("g").attr("class", "axis")
    .attr("transform", `translate(0,${innerH})`)
    .call(d3.axisBottom(x).ticks(5).tickSizeOuter(0));
  g.append("g").attr("class", "axis").call(d3.axisLeft(y).tickSizeOuter(0));

  const tip = ensureTooltip();

  g.selectAll("rect").data(rows).enter().append("rect")
    .attr("x", 0)
    .attr("y", (d) => y(d.category))
    .attr("height", y.bandwidth())
    .attr("width", (d) => x(d.count))
    .attr("fill", (d) => (colors && colors[d.category]) || "#CC0000")
    .on("mousemove", (event, d) => showTooltip(tip, event, `${d.category}: ${d.count.toLocaleString()}`))
    .on("mouseout", () => hideTooltip(tip));

  g.selectAll(".bar-label").data(rows).enter().append("text")
    .attr("class", "bar-label")
    .attr("x", (d) => x(d.count) + 6)
    .attr("y", (d) => y(d.category) + y.bandwidth() / 2)
    .attr("dy", "0.35em")
    .text((d) => d.count.toLocaleString());
}
