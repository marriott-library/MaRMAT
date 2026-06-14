/* Word Cloud of matched terms using d3-cloud (d3.layout.cloud).
   data: [{text, value}]. */

function renderWordCloud(selector, data) {
  const container = document.querySelector(selector);
  container.innerHTML = "";
  if (!data || !data.length) {
    container.innerHTML = '<div class="chart-empty">No term data</div>';
    return;
  }

  const width = container.clientWidth || 460;
  const height = 320;

  const maxValue = d3.max(data, (d) => d.value);
  const minValue = d3.min(data, (d) => d.value);
  // Square-root scaling keeps very frequent terms from dominating entirely.
  const sizeScale = d3.scaleSqrt().domain([minValue, maxValue]).range([13, 64]);

  const palette = ["#CC0000", "#890000", "#2B6CB0", "#2F855A", "#B7791F",
    "#6B46C1", "#C05621", "#0987A0", "#97266D", "#4A5568"];

  const words = data.map((d) => ({ text: d.text, value: d.value, size: sizeScale(d.value) }));

  const layout = d3.layout.cloud()
    .size([width, height])
    .words(words)
    .padding(2)
    .rotate(() => (Math.random() < 0.5 ? 0 : 90))
    .font("Segoe UI")
    .fontSize((d) => d.size)
    .on("end", draw);

  layout.start();

  function draw(laidOut) {
    const svg = d3.select(container).append("svg")
      .attr("class", "chart-svg")
      .attr("viewBox", `0 0 ${width} ${height}`);
    const g = svg.append("g").attr("transform", `translate(${width / 2},${height / 2})`);
    const tip = ensureTooltip();

    g.selectAll("text").data(laidOut).enter().append("text")
      .style("font-family", "Segoe UI, sans-serif")
      .style("font-weight", "600")
      .style("fill", (d, i) => palette[i % palette.length])
      .attr("text-anchor", "middle")
      .attr("font-size", (d) => d.size + "px")
      .attr("transform", (d) => `translate(${d.x},${d.y}) rotate(${d.rotate})`)
      .text((d) => d.text)
      .on("mousemove", (event, d) => showTooltip(tip, event, `${d.text}: ${d.value.toLocaleString()}`))
      .on("mouseout", () => hideTooltip(tip));
  }
}
