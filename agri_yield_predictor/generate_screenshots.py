"""
generate_screenshots.py
Generates programmatic UI-style screenshots using matplotlib.
Renders: landing page mockup, prediction form, analytics dashboard,
         model metrics panel, and API response view.
"""
import os, json, textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SS_DIR   = os.path.join(BASE_DIR, "screenshots")
REP_DIR  = os.path.join(BASE_DIR, "reports")
os.makedirs(SS_DIR, exist_ok=True)

API = "http://localhost:5000"

# ── Helpers ─────────────────────────────────────────────────────────────────
def add_navbar(ax, title="AgriYield AI"):
    ax.add_patch(FancyBboxPatch((0, 0.92), 1, 0.08, transform=ax.transAxes,
        boxstyle="square,pad=0", facecolor="#1a3a2a", zorder=5,
        clip_on=False))
    ax.text(0.02, 0.96, f"🌾  {title}", transform=ax.transAxes,
            color="#6ee67b", fontsize=13, fontweight="bold", va="center", zorder=6)
    for i, lbl in enumerate(["Predict", "Analytics", "Metrics"]):
        ax.text(0.72 + i*0.09, 0.96, lbl, transform=ax.transAxes,
                color="#d1fae5", fontsize=8, va="center", zorder=6)
    ax.text(0.96, 0.96, "✓ Live", transform=ax.transAxes,
            color="#065f46", fontsize=8, va="center", ha="right",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#d1fae5", edgecolor="none"),
            zorder=6)

def card(ax, x, y, w, h, title="", color="#fff", border="#e5e7eb"):
    r = FancyBboxPatch((x, y), w, h, transform=ax.transAxes,
        boxstyle="round,pad=0.01", facecolor=color, edgecolor=border, linewidth=1, zorder=2)
    ax.add_patch(r)
    if title:
        ax.text(x + 0.015, y + h - 0.035, title, transform=ax.transAxes,
                fontsize=9, fontweight="bold", color="#374151", zorder=3)

# ── Screenshot 1: Hero / Landing Page ───────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 7))
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
fig.patch.set_facecolor("#f0f4f8")
ax.set_facecolor("#f0f4f8")

add_navbar(ax)

# Hero gradient panel
hero = FancyBboxPatch((0, 0.60), 1, 0.31, transform=ax.transAxes,
    boxstyle="square,pad=0", facecolor="#2d6a4f", zorder=1)
ax.add_patch(hero)
ax.text(0.5, 0.80, "Agricultural Yield Predictor", transform=ax.transAxes,
        ha="center", va="center", fontsize=22, fontweight="bold", color="white", zorder=2)
ax.text(0.5, 0.72, "Machine-learning powered crop yield forecasting\nusing weather, soil & farm parameters",
        transform=ax.transAxes, ha="center", va="center",
        fontsize=11, color="#d1fae5", zorder=2)

# Stat cards
stats = [("4,000", "Farm Records"), ("28", "Features"), ("96.5%", "Model R²"), ("4", "ML Models")]
for i, (val, lbl) in enumerate(stats):
    cx = 0.06 + i * 0.235
    card(ax, cx, 0.38, 0.20, 0.18, color="#fff")
    ax.text(cx + 0.10, 0.50, val, transform=ax.transAxes, ha="center",
            fontsize=18, fontweight="bold", color="#2d6a4f", zorder=3)
    ax.text(cx + 0.10, 0.42, lbl, transform=ax.transAxes, ha="center",
            fontsize=9, color="#57606a", zorder=3)

# Feature list
features = ["🌧  Weather-aware predictions",
            "🌱  Soil NPK analysis",
            "💧  Irrigation method impact",
            "🤖  RandomForest model",
            "📊  Interactive analytics"]
for i, feat in enumerate(features):
    ax.text(0.05 + (i % 3) * 0.33, 0.28 - (i // 3) * 0.09, feat,
            transform=ax.transAxes, fontsize=9, color="#374151",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#d1fae5", edgecolor="none"))

plt.tight_layout(pad=0)
plt.savefig(os.path.join(SS_DIR, "ui_landing.png"), dpi=150, bbox_inches="tight")
plt.close()
print("  Saved: ui_landing.png")

# ── Screenshot 2: Prediction Form ───────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 8))
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
fig.patch.set_facecolor("#f0f4f8"); ax.set_facecolor("#f0f4f8")
add_navbar(ax)

ax.text(0.02, 0.88, "🔮  Yield Prediction", transform=ax.transAxes,
        fontsize=14, fontweight="bold", color="#1f2328",
        bbox=dict(boxstyle="square,pad=0", facecolor="none",
                  edgecolor="#2d6a4f", linewidth=3))

card(ax, 0.01, 0.07, 0.98, 0.79, color="#fff")

# Form fields
fields = [
    ("Crop", "Rice"),           ("Season", "Kharif"),       ("State", "Telangana"),
    ("District", "Warangal"),   ("Irrigation", "Drip"),     ("Farm Area (Ha)", "5.0"),
    ("Rainfall (mm)", "700"),   ("Temperature (°C)", "29"), ("Humidity (%)", "70"),
    ("Sunlight Hrs/Day", "7"),  ("Soil pH", "6.2"),         ("Soil Moisture", "28"),
    ("Nitrogen kg/ha", "120"),  ("Phosphorus kg/ha", "55"), ("Potassium kg/ha", "110"),
    ("Fertilizer kg/ha", "180"),("Pesticide L/ha", "5"),    ("Seed Quality", "0.9"),
    ("Water Used m3", "3000"),  ("Disease Risk %", "35"),
]
cols = 4
for idx, (label, val) in enumerate(fields):
    col = idx % cols
    row = idx // cols
    fx = 0.03 + col * 0.245
    fy = 0.73 - row * 0.14
    ax.text(fx, fy + 0.05, label.upper(), transform=ax.transAxes,
            fontsize=6.5, color="#57606a", fontweight="bold")
    rect = FancyBboxPatch((fx, fy), 0.22, 0.045, transform=ax.transAxes,
        boxstyle="round,pad=0.005", facecolor="#f9fafb", edgecolor="#d1d5db", zorder=3)
    ax.add_patch(rect)
    ax.text(fx + 0.01, fy + 0.022, val, transform=ax.transAxes,
            fontsize=8.5, color="#1f2328", va="center", zorder=4)

# Predict button
btn = FancyBboxPatch((0.35, 0.10), 0.30, 0.05, transform=ax.transAxes,
    boxstyle="round,pad=0.01", facecolor="#2d6a4f", edgecolor="none", zorder=3)
ax.add_patch(btn)
ax.text(0.50, 0.125, "Predict Yield", transform=ax.transAxes,
        ha="center", va="center", color="white", fontsize=11, fontweight="bold", zorder=4)

# Result box
res = FancyBboxPatch((0.65, 0.10), 0.33, 0.12, transform=ax.transAxes,
    boxstyle="round,pad=0.01", facecolor="#f0fdf4", edgecolor="#6ee67b", linewidth=2, zorder=3)
ax.add_patch(res)
ax.text(0.815, 0.195, "PREDICTED YIELD", transform=ax.transAxes,
        ha="center", fontsize=7, color="#065f46", fontweight="bold", zorder=4)
ax.text(0.815, 0.155, "3.142", transform=ax.transAxes,
        ha="center", fontsize=20, color="#065f46", fontweight="bold", zorder=4)
ax.text(0.815, 0.118, "Tonnes / Hectare", transform=ax.transAxes,
        ha="center", fontsize=8, color="#6b7280", zorder=4)

plt.tight_layout(pad=0)
plt.savefig(os.path.join(SS_DIR, "ui_predict_form.png"), dpi=150, bbox_inches="tight")
plt.close()
print("  Saved: ui_predict_form.png")

# ── Screenshot 3: Analytics Dashboard ───────────────────────────────────────
crops_data = requests.get(f"{API}/api/crop_analysis").json()
season_data = requests.get(f"{API}/api/season_analysis").json()

fig = plt.figure(figsize=(14, 8))
fig.patch.set_facecolor("#f0f4f8")

# Subplot layout
ax_nav = fig.add_axes([0, 0.93, 1, 0.07]); ax_nav.axis("off")
ax_nav.set_facecolor("#1a3a2a")
ax_nav.text(0.02, 0.5, "🌾  AgriYield AI — Analytics", color="#6ee67b",
            fontsize=13, fontweight="bold", va="center")
ax_nav.text(0.96, 0.5, "✓ Live", color="#065f46", fontsize=8, va="center", ha="right",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#d1fae5", edgecolor="none"))

ax1 = fig.add_axes([0.04, 0.52, 0.44, 0.37])
ax2 = fig.add_axes([0.54, 0.52, 0.44, 0.37])
ax3 = fig.add_axes([0.04, 0.06, 0.92, 0.38])

# Crop bar
crop_names  = [c["Crop"] for c in crops_data]
crop_yields = [c["Mean_Yield"] for c in crops_data]
colors = plt.cm.Set2(np.linspace(0, 1, len(crop_names)))
ax1.bar(crop_names, crop_yields, color=colors)
ax1.set_title("Mean Yield by Crop", fontsize=11, fontweight="bold")
ax1.set_ylabel("Yield (T/Ha)"); ax1.set_xlabel("Crop")
ax1.tick_params(axis='x', rotation=15)
ax1.set_facecolor("#fff")

# Season donut
season_names = [s["Season"] for s in season_data]
season_means = [s["Mean_Yield"] for s in season_data]
wedges, texts, autotexts = ax2.pie(season_means, labels=season_names,
    autopct="%1.1f%%", colors=plt.cm.Set3(np.linspace(0, 1, len(season_names))),
    wedgeprops=dict(width=0.55))
ax2.set_title("Yield Share by Season", fontsize=11, fontweight="bold")

# State bar (top 10)
state_data = requests.get(f"{API}/api/state_analysis").json()[:10]
states = [s["State"] for s in state_data]
s_yields = [s["Mean_Yield"] for s in state_data]
bars = ax3.barh(states[::-1], s_yields[::-1],
                color=plt.cm.Blues(np.linspace(0.4, 0.9, len(states))))
ax3.set_title("Top 10 States by Mean Yield", fontsize=11, fontweight="bold")
ax3.set_xlabel("Mean Yield (T/Ha)")
ax3.set_facecolor("#fff")
for bar, v in zip(bars, s_yields[::-1]):
    ax3.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
             f"{v:.2f}", va="center", fontsize=8)

for a in [ax1, ax2, ax3]:
    a.spines['top'].set_visible(False); a.spines['right'].set_visible(False)

plt.savefig(os.path.join(SS_DIR, "ui_analytics.png"), dpi=150, bbox_inches="tight")
plt.close()
print("  Saved: ui_analytics.png")

# ── Screenshot 4: Model Metrics Panel ───────────────────────────────────────
metrics = requests.get(f"{API}/api/model_metrics").json()

fig, axes = plt.subplots(1, 4, figsize=(14, 5))
fig.patch.set_facecolor("#f0f4f8")
fig.suptitle("Model Performance Comparison", fontsize=16, fontweight="bold", y=0.98)

metric_keys = ["RMSE", "MAE", "R2", "CV_R2"]
metric_labels = ["RMSE (lower better)", "MAE (lower better)",
                 "R² (higher better)", "Cross-Val R²"]
model_names = list(metrics.keys())
pal = ["#3b82d4", "#7c5cd8", "#22c55e", "#f59e0b"]

for i, (mkey, mlabel) in enumerate(zip(metric_keys, metric_labels)):
    ax = axes[i]
    vals = [metrics[m][mkey] for m in model_names]
    bars = ax.bar(model_names, vals, color=pal)
    ax.set_title(mlabel, fontsize=9, fontweight="bold")
    ax.set_facecolor("#fff")
    ax.tick_params(axis='x', rotation=20, labelsize=8)
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    best_idx = vals.index(min(vals) if "lower" in mlabel else max(vals))
    bars[best_idx].set_edgecolor("#f59e0b"); bars[best_idx].set_linewidth(3)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01*max(vals),
                f"{v:.3f}", ha="center", fontsize=7.5)

plt.tight_layout()
plt.savefig(os.path.join(SS_DIR, "ui_metrics.png"), dpi=150, bbox_inches="tight")
plt.close()
print("  Saved: ui_metrics.png")

# ── Screenshot 5: API Response View ─────────────────────────────────────────
api_out_path = os.path.join(REP_DIR, "api_outputs.json")
with open(api_out_path) as f:
    api_data = json.load(f)

fig, ax = plt.subplots(figsize=(12, 8))
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
fig.patch.set_facecolor("#1e1e1e"); ax.set_facecolor("#1e1e1e")

ax.text(0.5, 0.96, "API Response Explorer", ha="center", fontsize=14,
        fontweight="bold", color="#6ee67b", transform=ax.transAxes)

# Show key endpoints as terminal cards
snippets = [
    ("GET /api/health",
     json.dumps(api_data.get("/api/health", {}).get("data", {}), indent=2)[:200]),
    ("POST /api/predict",
     json.dumps(api_data.get("/api/predict", {}).get("data", {}), indent=2)[:200]),
    ("GET /api/model_metrics",
     json.dumps({k: v for k, v in list(
         api_data.get("/api/model_metrics", {}).get("data", {}).items())[:2]}, indent=2)[:300]),
]

y_pos = 0.88
for endpoint, text in snippets:
    bg = FancyBboxPatch((0.02, y_pos - 0.24), 0.96, 0.26, transform=ax.transAxes,
        boxstyle="round,pad=0.01", facecolor="#2d2d2d", edgecolor="#444", zorder=2)
    ax.add_patch(bg)
    ax.text(0.04, y_pos - 0.01, endpoint, transform=ax.transAxes,
            fontsize=9, fontweight="bold", color="#61dafb", zorder=3,
            fontfamily="monospace")
    ax.text(0.04, y_pos - 0.225, text, transform=ax.transAxes,
            fontsize=7.5, color="#98c379", zorder=3, va="bottom",
            fontfamily="monospace")
    y_pos -= 0.31

plt.tight_layout(pad=0)
plt.savefig(os.path.join(SS_DIR, "ui_api_response.png"), dpi=150, bbox_inches="tight")
plt.close()
print("  Saved: ui_api_response.png")

print("\nAll UI screenshots saved to screenshots/")
