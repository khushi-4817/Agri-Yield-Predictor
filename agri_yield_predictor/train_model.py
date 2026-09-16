"""
Agricultural Yield Predictor - ML Training Script
Dataset: Seasonal Agriculture Performance Dataset
Target: Yield_Tonnes_Ha (regression)
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.pipeline import Pipeline

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "agriculture_dataset.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

# ─── Load Data ────────────────────────────────────────────────────────────────
print("Loading dataset …")
df = pd.read_csv(DATA_PATH)
print(f"  Shape: {df.shape}")
print(f"  Columns: {list(df.columns)}")

# ─── Feature Engineering ─────────────────────────────────────────────────────
CATEGORICAL_COLS = ["State", "District", "Crop", "Season", "Irrigation_Method"]
NUMERIC_FEATURES = [
    "Farm_Area_Hectares", "Rainfall_mm", "Avg_Temperature_C", "Humidity_pct",
    "Sunlight_Hours_Day", "Soil_pH", "Soil_Moisture_pct",
    "Nitrogen_kg_ha", "Phosphorus_kg_ha", "Potassium_kg_ha",
    "Fertilizer_kg_ha", "Pesticide_Litre_ha", "Seed_Quality_Score",
    "Water_Used_m3", "Disease_Pest_Risk_pct"
]
TARGET = "Yield_Tonnes_Ha"

# Drop rows with missing target or feature values
df = df.dropna(subset=[TARGET] + NUMERIC_FEATURES + CATEGORICAL_COLS).reset_index(drop=True)
print(f"  Rows after dropna: {len(df)}")


# Encode categoricals
label_encoders = {}
df_enc = df.copy()
for col in CATEGORICAL_COLS:
    le = LabelEncoder()
    df_enc[col] = le.fit_transform(df_enc[col].astype(str))
    label_encoders[col] = le

FEATURE_COLS = NUMERIC_FEATURES + CATEGORICAL_COLS
X = df_enc[FEATURE_COLS]
y = df_enc[TARGET]

# ─── Train / Test Split ───────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"  Train: {len(X_train)} | Test: {len(X_test)}")

# ─── Train Models ─────────────────────────────────────────────────────────────
models = {
    "RandomForest":        RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1),
    "GradientBoosting":    GradientBoostingRegressor(n_estimators=200, random_state=42),
    "Ridge":               Pipeline([("scaler", StandardScaler()), ("ridge", Ridge(alpha=1.0))]),
    "LinearRegression":    Pipeline([("scaler", StandardScaler()), ("lr", LinearRegression())])
}

results = {}
print("\nTraining models …")
for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    rmse  = np.sqrt(mean_squared_error(y_test, y_pred))
    mae   = mean_absolute_error(y_test, y_pred)
    r2    = r2_score(y_test, y_pred)
    cv    = cross_val_score(model, X, y, cv=5, scoring="r2").mean()
    results[name] = {"RMSE": round(rmse, 4), "MAE": round(mae, 4),
                     "R2": round(r2, 4), "CV_R2": round(cv, 4)}
    print(f"  {name:22s}  RMSE={rmse:.4f}  MAE={mae:.4f}  R²={r2:.4f}  CV-R²={cv:.4f}")

# ─── Select Best Model ────────────────────────────────────────────────────────
best_name = max(results, key=lambda n: results[n]["R2"])
best_model = models[best_name]
print(f"\nBest model: {best_name} (R²={results[best_name]['R2']})")

# ─── Save Artifacts ───────────────────────────────────────────────────────────
joblib.dump(best_model, os.path.join(MODEL_DIR, "best_model.pkl"))
joblib.dump(label_encoders, os.path.join(MODEL_DIR, "label_encoders.pkl"))

meta = {
    "best_model": best_name,
    "feature_cols": FEATURE_COLS,
    "categorical_cols": CATEGORICAL_COLS,
    "numeric_features": NUMERIC_FEATURES,
    "target": TARGET,
    "metrics": results,
    "unique_values": {col: sorted(df[col].astype(str).unique().tolist())
                      for col in CATEGORICAL_COLS}
}
with open(os.path.join(MODEL_DIR, "model_meta.json"), "w") as f:
    json.dump(meta, f, indent=2)
print("  Artifacts saved to models/")

# ─── Plots ────────────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", palette="muted")

# 1. Model comparison bar chart
fig, ax = plt.subplots(figsize=(8, 4))
names = list(results.keys())
r2_vals = [results[n]["R2"] for n in names]
bars = ax.barh(names, r2_vals, color=["#3b82d4","#7c5cd8","#22c55e","#f59e0b"])
ax.set_xlabel("R² Score")
ax.set_title("Model Comparison — R² on Test Set")
for bar, val in zip(bars, r2_vals):
    ax.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height()/2,
            f"{val:.3f}", va="center", fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(SCREENSHOTS_DIR, "model_comparison.png"), dpi=150)
plt.close()

# 2. Actual vs Predicted scatter
y_pred_best = best_model.predict(X_test)
fig, ax = plt.subplots(figsize=(6, 5))
ax.scatter(y_test, y_pred_best, alpha=0.4, color="#3b82d4", edgecolors="none", s=20)
mn, mx = y_test.min(), y_test.max()
ax.plot([mn, mx], [mn, mx], "r--", lw=1.5, label="Perfect fit")
ax.set_xlabel("Actual Yield (Tonnes/Ha)")
ax.set_ylabel("Predicted Yield (Tonnes/Ha)")
ax.set_title(f"Actual vs Predicted — {best_name}")
ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(SCREENSHOTS_DIR, "actual_vs_predicted.png"), dpi=150)
plt.close()

# 3. Feature importance (RF / GB only)
if hasattr(best_model, "feature_importances_"):
    importances = best_model.feature_importances_
    feat_df = pd.DataFrame({"Feature": FEATURE_COLS, "Importance": importances})
    feat_df = feat_df.sort_values("Importance", ascending=True).tail(15)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(feat_df["Feature"], feat_df["Importance"], color="#3b82d4")
    ax.set_xlabel("Importance")
    ax.set_title("Top-15 Feature Importances")
    plt.tight_layout()
    plt.savefig(os.path.join(SCREENSHOTS_DIR, "feature_importance.png"), dpi=150)
    plt.close()

# 4. Yield distribution by crop
fig, ax = plt.subplots(figsize=(9, 4))
crop_order = df.groupby("Crop")["Yield_Tonnes_Ha"].median().sort_values().index
sns.boxplot(data=df, x="Crop", y="Yield_Tonnes_Ha", order=crop_order, ax=ax,
            hue="Crop", palette="Set2", legend=False)
ax.set_xlabel("Crop")
ax.set_ylabel("Yield (Tonnes/Ha)")
ax.set_title("Yield Distribution by Crop")
plt.tight_layout()
plt.savefig(os.path.join(SCREENSHOTS_DIR, "yield_by_crop.png"), dpi=150)
plt.close()

# 5. Correlation heatmap
fig, ax = plt.subplots(figsize=(10, 8))
corr = df[NUMERIC_FEATURES + [TARGET]].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt=".1f", cmap="coolwarm",
            linewidths=0.3, ax=ax, cbar_kws={"shrink": 0.7})
ax.set_title("Feature Correlation Heatmap")
plt.tight_layout()
plt.savefig(os.path.join(SCREENSHOTS_DIR, "correlation_heatmap.png"), dpi=150)
plt.close()

print("\nAll plots saved to screenshots/")
print("\nTraining complete!")
