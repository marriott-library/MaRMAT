/* Statistics dashboard orchestrator: fetch /api/statistics, render KPIs + 4 charts. */

(function () {
  const statusEl = document.getElementById("stats-status");

  function renderKpis(kpis) {
    const set = (id, value) => { document.getElementById(id).textContent = value; };
    set("kpi-total", kpis.totalFlagged.toLocaleString());
    set("kpi-collections", kpis.uniqueCollections.toLocaleString());
    set("kpi-terms", kpis.uniqueTerms.toLocaleString());
    set("kpi-category", kpis.mostFrequentCategory);
    set("kpi-term", kpis.mostFrequentTerm);
  }

  function renderAll(stats) {
    renderKpis(stats.kpis);
    renderCategoryBar("#chart-category", stats.categoryDistribution, stats.categoryColors);
    renderTopTermsBar("#chart-terms", "#legend-terms", stats.topTerms, stats.categoryColors);
    renderColumnPie("#chart-columns", "#legend-columns", stats.columnDistribution);
    renderWordCloud("#chart-wordcloud", stats.wordCloud);
  }

  async function load() {
    try {
      const stats = await MaRMAT.getJSON("/api/statistics");
      if (!stats.hasData) {
        MaRMAT.notice(statusEl, "info",
          "No results available yet. Run an analysis to see statistics.");
        document.getElementById("dashboard").hidden = true;
        return;
      }
      statusEl.hidden = true;
      document.getElementById("dashboard").hidden = false;
      renderAll(stats);
      window.__marmatStats = stats; // for resize re-render
    } catch (err) {
      MaRMAT.notice(statusEl, "error", err.message);
    }
  }

  // Re-render on resize (debounced) so charts stay responsive.
  let resizeTimer = null;
  window.addEventListener("resize", () => {
    if (!window.__marmatStats) return;
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => renderAll(window.__marmatStats), 200);
  });

  load();
})();
