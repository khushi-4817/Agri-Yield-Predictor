/* app.js — Agricultural Yield Predictor Frontend */
const API = "";   // same origin

let metaData    = null;
let stateChart  = null;

// ── On Load ───────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", async () => {
  await checkHealth();
  await loadMeta();
  await loadAnalytics();
  await loadMetrics();
  document.getElementById("predict-form").addEventListener("submit", handlePredict);
});

// ── Health ─────────────────────────────────────────────────────────────────────
async function checkHealth() {
  const badge = document.getElementById("status-badge");
  try {
    const res  = await fetch(`${API}/api/health`);
    const data = await res.json();
    if (data.status === "ok") {
      badge.textContent = `✓ Live — ${data.model}`;
      badge.className   = "badge badge-ok";
    }
  } catch {
    badge.textContent = "✗ Offline";
    badge.className   = "badge badge-error";
  }
}

// ── Meta / Populate selects ────────────────────────────────────────────────────
async function loadMeta() {
  const res  = await fetch(`${API}/api/meta`);
  metaData   = await res.json();
  const uvs  = metaData.unique_values;
  populateSelect("Crop",              uvs["Crop"]             || []);
  populateSelect("Season",            uvs["Season"]           || []);
  populateSelect("State",             uvs["State"]            || []);
  populateSelect("District",          uvs["District"]         || []);
  populateSelect("Irrigation_Method", uvs["Irrigation_Method"]|| []);
}

function populateSelect(id, values) {
  const el = document.getElementById(id);
  if (!el) return;
  el.innerHTML = values.map(v => `<option value="${v}">${v}</option>`).join("");
}

// ── Predict ────────────────────────────────────────────────────────────────────
async function handlePredict(e) {
  e.preventDefault();
  const btn = e.target.querySelector("button[type=submit]");
  btn.textContent = "Predicting…";
  btn.disabled    = true;

  const fd  = new FormData(e.target);
  const body = {};
  fd.forEach((v, k) => { body[k] = isNaN(v) || v === "" ? v : parseFloat(v); });

  try {
    const res  = await fetch(`${API}/api/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    const data = await res.json();
    const box  = document.getElementById("result-box");
    box.classList.remove("hidden");
    document.getElementById("result-value").textContent =
      data.predicted_yield_tonnes_ha !== undefined
        ? data.predicted_yield_tonnes_ha.toFixed(3)
        : "Error";
    document.getElementById("result-model").textContent =
      `Model: ${data.model || ""}`;
  } catch (err) {
    alert("Prediction failed: " + err.message);
  } finally {
    btn.textContent = "Predict Yield";
    btn.disabled    = false;
  }
}

// ── Analytics ──────────────────────────────────────────────────────────────────
async function loadAnalytics() {
  const [cropRes, seasonRes, stateRes] = await Promise.all([
    fetch(`${API}/api/crop_analysis`),
    fetch(`${API}/api/season_analysis`),
    fetch(`${API}/api/state_analysis`)
  ]);
  const crops   = await cropRes.json();
  const seasons = await seasonRes.json();
  const states  = await stateRes.json();

  renderTable("crop-table",   crops,
    ["Crop","Mean_Yield","Median_Yield","Std_Yield","Count"]);
  renderTable("season-table", seasons,
    ["Season","Mean_Yield","Median_Yield","Std_Yield","Count"]);
  renderStateChart(states.slice(0, 12));
}

function renderTable(containerId, rows, cols) {
  const container = document.getElementById(containerId);
  if (!container || !rows.length) return;
  const header = `<tr>${cols.map(c => `<th>${c.replace(/_/g," ")}</th>`).join("")}</tr>`;
  const body   = rows.map(r =>
    `<tr>${cols.map(c => `<td>${typeof r[c] === "number" ? r[c].toFixed(3) : r[c]}</td>`).join("")}</tr>`
  ).join("");
  container.innerHTML = `<table><thead>${header}</thead><tbody>${body}</tbody></table>`;
}

function renderStateChart(states) {
  const ctx = document.getElementById("state-chart").getContext("2d");
  if (stateChart) stateChart.destroy();
  stateChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: states.map(s => s.State),
      datasets: [{
        label: "Mean Yield (T/Ha)",
        data:  states.map(s => s.Mean_Yield),
        backgroundColor: states.map((_, i) =>
          `hsl(${140 + i * 8}, 55%, ${45 + i}%)`),
        borderRadius: 6
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { y: { title: { display: true, text: "Mean Yield (T/Ha)" } } }
    }
  });
}

// ── Metrics ────────────────────────────────────────────────────────────────────
async function loadMetrics() {
  const res     = await fetch(`${API}/api/model_metrics`);
  const metrics = await res.json();
  const best    = Object.entries(metrics).sort((a,b) => b[1].R2 - a[1].R2)[0][0];
  const grid    = document.getElementById("metrics-cards");
  grid.innerHTML = Object.entries(metrics).map(([name, m]) => `
    <div class="metric-card ${name === best ? "best" : ""}">
      <div class="metric-name">${name}</div>
      <div class="metric-row"><span>RMSE</span><span>${m.RMSE}</span></div>
      <div class="metric-row"><span>MAE</span><span>${m.MAE}</span></div>
      <div class="metric-row"><span>R²</span><span>${m.R2}</span></div>
      <div class="metric-row"><span>CV R²</span><span>${m.CV_R2}</span></div>
      ${name === best ? '<div class="best-badge">⭐ Best Model</div>' : ""}
    </div>`).join("");
}
