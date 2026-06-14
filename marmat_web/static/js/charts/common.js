/* Shared chart helpers: a single reusable D3 tooltip. */

function ensureTooltip() {
  let tip = document.getElementById("d3-tooltip");
  if (!tip) {
    tip = document.createElement("div");
    tip.id = "d3-tooltip";
    tip.className = "d3-tooltip";
    document.body.appendChild(tip);
  }
  return tip;
}

function showTooltip(tip, event, html) {
  tip.innerHTML = html;
  tip.style.left = event.pageX + 12 + "px";
  tip.style.top = event.pageY + 12 + "px";
  tip.style.opacity = "1";
}

function hideTooltip(tip) {
  tip.style.opacity = "0";
}
