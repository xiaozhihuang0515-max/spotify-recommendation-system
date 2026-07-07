const fmt = new Intl.NumberFormat();
const $ = (selector) => document.querySelector(selector);

async function getJSON(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Request failed: ${response.status}`);
  return response.json();
}

function renderMetrics(summary) {
  const items = [
    [fmt.format(summary.tracks), "tracks"],
    [fmt.format(summary.artists), "artists"],
    [summary.genres, "genres"],
    [summary.avg_popularity, "avg popularity"],
  ];
  $("#metrics").innerHTML = items.map(([value, label]) =>
    `<div class="metric"><b>${value}</b><span>${label}</span></div>`).join("");
}

function renderCharts(data) {
  const maxPopularity = Math.max(...data.genres.map(item => item.avg_popularity));
  $("#genre-chart").innerHTML = data.genres.map(item => `
    <div class="genre-row"><strong>${item.genre}</strong>
      <div class="bar-track"><div class="bar" style="width:${100 * item.avg_popularity / maxPopularity}%"></div></div>
      <small>${item.avg_popularity}</small></div>`).join("");
  const maxCount = Math.max(...data.popularity.map(item => item.count));
  $("#histogram").innerHTML = data.popularity.map(item =>
    `<div class="hist-col" title="${item.count} tracks" style="height:${100 * item.count / maxCount}%"><span>${item.label.split("–")[0]}</span></div>`
  ).join("");
}

function resultButton(item, recommendation = false) {
  return `<button class="result" data-id="${item.track_id}">
    <span><strong>${item.track_name}</strong><br><small>${item.artists}${item.genre ? ` · ${item.genre}` : ""}</small></span>
    ${recommendation ? `<span class="score">${Math.round(item.similarity * 100)}%</span>` : "<span>→</span>"}
  </button>`;
}

async function search() {
  const query = $("#search").value.trim();
  const results = await getJSON(`/api/tracks?q=${encodeURIComponent(query)}&limit=8`);
  $("#results").innerHTML = results.length
    ? results.map(item => resultButton(item)).join("")
    : '<p class="muted">No matching tracks.</p>';
}

$("#search-button").addEventListener("click", search);
$("#search").addEventListener("keydown", event => { if (event.key === "Enter") search(); });
$("#results").addEventListener("click", async event => {
  const button = event.target.closest("[data-id]");
  if (!button) return;
  $("#results").innerHTML = '<p class="muted">Mapping the neighborhood…</p>';
  const data = await getJSON(`/api/recommend/${button.dataset.id}`);
  $("#results").innerHTML = `<p><strong>Similar to ${data.source.track_name}</strong></p>` +
    data.recommendations.map(item => resultButton(item, true)).join("");
});

Promise.all([getJSON("/api/summary"), getJSON("/api/visualizations")])
  .then(([summary, charts]) => { renderMetrics(summary); renderCharts(charts); })
  .catch(error => { document.body.insertAdjacentHTML("afterbegin", `<p>${error.message}</p>`); });

