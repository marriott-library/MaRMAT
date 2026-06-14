/* Shared helpers for the MaRMAT web app. */

const MaRMAT = {
  /** POST JSON and return parsed response (throws on non-OK with .error). */
  async postJSON(url, body) {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body || {}),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || `Request failed (${res.status})`);
    return data;
  },

  /** GET JSON. */
  async getJSON(url) {
    const res = await fetch(url);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || `Request failed (${res.status})`);
    return data;
  },

  /** Upload a single file via multipart form. extraFields is an object. */
  async uploadFile(url, file, extraFields) {
    const form = new FormData();
    form.append("file", file);
    for (const [k, v] of Object.entries(extraFields || {})) form.append(k, v);
    const res = await fetch(url, { method: "POST", body: form });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || `Upload failed (${res.status})`);
    return data;
  },

  /** Render a {columns, rows} preview into a container as a scrollable table. */
  renderTable(container, preview) {
    if (!preview || !preview.columns || preview.columns.length === 0) {
      container.innerHTML = '<p class="muted">No data to preview.</p>';
      return;
    }
    const thead = "<tr>" + preview.columns.map((c) => `<th>${MaRMAT.esc(c)}</th>`).join("") + "</tr>";
    const tbody = preview.rows
      .map((row) => "<tr>" + row.map((cell) => `<td>${MaRMAT.esc(cell)}</td>`).join("") + "</tr>")
      .join("");
    container.innerHTML =
      `<div class="table-wrap"><table class="data"><thead>${thead}</thead><tbody>${tbody}</tbody></table></div>`;
  },

  esc(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  },

  /** Show a transient notice in an element (type: info|warn|error|success). */
  notice(el, type, message) {
    if (!el) return;
    el.className = `notice notice--${type}`;
    el.textContent = message;
    el.hidden = false;
  },
};
