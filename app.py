"""
Agricultural Yield Predictor — Flask Backend
Run from Project root:  python app.py
  http://localhost:5000/           → Prediction UI
  http://localhost:5000/dashboard  → Analytics Dashboard
API endpoints: /api/health, /api/meta, /api/predict, /api/batch_predict,
               /api/stats, /api/model_metrics, /api/crop_analysis,
               /api/season_analysis, /api/state_analysis
"""

import os, json
import joblib
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# ─── Paths — everything inside agri_yield_predictor/ ──────────────────────────
ROOT      = os.path.dirname(os.path.abspath(__file__))          # Project root
BASE      = os.path.join(ROOT, "agri_yield_predictor")          # sub-project
MODEL_DIR = os.path.join(BASE, "models")
DATA_PATH = os.path.join(BASE, "data", "agriculture_dataset.csv")
TMPL_DIR  = os.path.join(BASE, "templates")
STATIC    = os.path.join(BASE, "static")

# ─── Flask app ─────────────────────────────────────────────────────────────────
app = Flask(__name__, template_folder=TMPL_DIR, static_folder=STATIC)
CORS(app)

# ─── Load ML artifacts ─────────────────────────────────────────────────────────
model          = joblib.load(os.path.join(MODEL_DIR, "best_model.pkl"))
label_encoders = joblib.load(os.path.join(MODEL_DIR, "label_encoders.pkl"))
with open(os.path.join(MODEL_DIR, "model_meta.json")) as f:
    meta = json.load(f)

df               = pd.read_csv(DATA_PATH)
FEATURE_COLS     = meta["feature_cols"]
CATEGORICAL_COLS = meta["categorical_cols"]
NUMERIC_FEATURES = meta["numeric_features"]

# ─── Helper ────────────────────────────────────────────────────────────────────
def encode_input(data: dict) -> pd.DataFrame:
    row = {}
    for col in NUMERIC_FEATURES:
        row[col] = float(data.get(col, 0))
    for col in CATEGORICAL_COLS:
        val = str(data.get(col, ""))
        le  = label_encoders[col]
        row[col] = int(le.transform([val])[0]) if val in le.classes_ else 0
    return pd.DataFrame([row], columns=FEATURE_COLS)

# ═══ Page Routes ═══════════════════════════════════════════════════════════════

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

# ═══ API Routes ════════════════════════════════════════════════════════════════

@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "model": meta["best_model"],
                    "dataset_rows": len(df)})

@app.route("/api/meta")
def get_meta():
    return jsonify({
        "best_model":       meta["best_model"],
        "feature_cols":     meta["feature_cols"],
        "categorical_cols": meta["categorical_cols"],
        "numeric_features": meta["numeric_features"],
        "target":           meta["target"],
        "unique_values":    meta["unique_values"]
    })

@app.route("/api/predict", methods=["POST"])
def predict():
    data = request.get_json(force=True)
    try:
        yp = float(model.predict(encode_input(data))[0])
        return jsonify({"predicted_yield_tonnes_ha": round(yp, 4),
                        "model": meta["best_model"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/batch_predict", methods=["POST"])
def batch_predict():
    records = request.get_json(force=True)
    if not isinstance(records, list):
        return jsonify({"error": "Expected a JSON array"}), 400
    try:
        X     = pd.concat([encode_input(r) for r in records], ignore_index=True)
        preds = model.predict(X)
        return jsonify({"predictions": [round(float(p), 4) for p in preds],
                        "count": len(preds)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/stats")
def stats():
    cols = ["Yield_Tonnes_Ha", "Farm_Area_Hectares", "Rainfall_mm",
            "Avg_Temperature_C", "Humidity_pct", "Soil_pH",
            "Fertilizer_kg_ha", "Profit_INR"]
    return jsonify(df[cols].describe().round(3).to_dict())

@app.route("/api/model_metrics")
def model_metrics():
    return jsonify(meta["metrics"])

@app.route("/api/crop_analysis")
def crop_analysis():
    agg = (df.groupby("Crop")["Yield_Tonnes_Ha"]
             .agg(["mean","median","std","min","max","count"])
             .round(4).reset_index())
    agg.columns = ["Crop","Mean_Yield","Median_Yield","Std_Yield","Min_Yield","Max_Yield","Count"]
    return jsonify(agg.to_dict(orient="records"))

@app.route("/api/season_analysis")
def season_analysis():
    agg = (df.groupby("Season")["Yield_Tonnes_Ha"]
             .agg(["mean","median","std","count"])
             .round(4).reset_index())
    agg.columns = ["Season","Mean_Yield","Median_Yield","Std_Yield","Count"]
    return jsonify(agg.to_dict(orient="records"))

@app.route("/api/state_analysis")
def state_analysis():
    agg = (df.groupby("State")["Yield_Tonnes_Ha"]
             .agg(["mean","median","count"])
             .round(4).reset_index()
             .sort_values("mean", ascending=False))
    agg.columns = ["State","Mean_Yield","Median_Yield","Count"]
    return jsonify(agg.to_dict(orient="records"))

# ═══ Entry Point ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print(f"  Templates : {TMPL_DIR}")
    print(f"  Static    : {STATIC}")
    print(f"  Models    : {MODEL_DIR}")
    print(f"  Data      : {DATA_PATH}")
    print(f"\n  UI        : http://localhost:5000/")
    print(f"  Dashboard : http://localhost:5000/dashboard")
    print(f"  API       : http://localhost:5000/api/health\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
