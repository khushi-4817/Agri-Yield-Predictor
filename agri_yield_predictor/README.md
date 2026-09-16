# 🌾 Agricultural Yield Predictor

A full-stack machine-learning application that predicts crop yield (Tonnes/Hectare) from weather, soil, and farm management parameters using the **Seasonal Agriculture Performance Dataset**.

---

## Project Structure

```
agri_yield_predictor/
├── data/
│   └── agriculture_dataset.csv      # Source dataset
├── models/
│   ├── best_model.pkl               # Trained ML model (generated)
│   ├── label_encoders.pkl           # Categorical encoders (generated)
│   └── model_meta.json              # Feature list & metrics (generated)
├── static/
│   ├── css/style.css
│   └── js/app.js
├── templates/
│   └── index.html
├── screenshots/                     # Auto-generated plots
├── reports/                         # Final Word report
├── train_model.py                   # ML training script
├── app.py                           # Flask backend API
├── generate_screenshots.py          # Programmatic UI screenshot generator
├── collect_api_outputs.py           # API output collector
├── generate_report.py               # Word report generator
└── requirements.txt
```

---

## Prerequisites

- Python 3.9+
- pip

---

## Quick Start

### 1. Install dependencies

```bash
cd agri_yield_predictor
pip install -r requirements.txt
```

### 2. Train the ML model

```bash
python train_model.py
```

This will:
- Train 4 models (RandomForest, GradientBoosting, Ridge, LinearRegression)
- Save the best model to `models/best_model.pkl`
- Generate EDA plots to `screenshots/`

### 3. Start the Flask backend

```bash
python app.py
```

Server starts at **http://localhost:5000**

### 4. Open the UI

Navigate to **http://localhost:5000** in your browser.

### 5. (Optional) Collect API outputs & generate report

```bash
# Collect all API endpoint outputs to JSON
python collect_api_outputs.py

# Generate programmatic UI screenshots
python generate_screenshots.py

# Build the Word project report
python generate_report.py
```

---

## API Endpoints

| Method | Endpoint              | Description                        |
|--------|-----------------------|------------------------------------|
| GET    | `/api/health`         | Health check & model name          |
| GET    | `/api/meta`           | Feature metadata & unique values   |
| POST   | `/api/predict`        | Single yield prediction            |
| POST   | `/api/batch_predict`  | Batch yield predictions            |
| GET    | `/api/stats`          | Dataset summary statistics         |
| GET    | `/api/model_metrics`  | All model RMSE / MAE / R² scores   |
| GET    | `/api/crop_analysis`  | Per-crop yield aggregation         |
| GET    | `/api/season_analysis`| Per-season yield aggregation       |
| GET    | `/api/state_analysis` | Per-state yield aggregation        |

---

## Sample Prediction Request

```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "Crop": "Rice", "Season": "Kharif", "State": "Telangana",
    "District": "Warangal", "Irrigation_Method": "Drip",
    "Farm_Area_Hectares": 5, "Rainfall_mm": 700,
    "Avg_Temperature_C": 29, "Humidity_pct": 70,
    "Sunlight_Hours_Day": 7, "Soil_pH": 6.2,
    "Soil_Moisture_pct": 28, "Nitrogen_kg_ha": 120,
    "Phosphorus_kg_ha": 55, "Potassium_kg_ha": 110,
    "Fertilizer_kg_ha": 180, "Pesticide_Litre_ha": 5,
    "Seed_Quality_Score": 0.9, "Water_Used_m3": 3000,
    "Disease_Pest_Risk_pct": 35
  }'
```

---

## Tech Stack

| Layer     | Technology                        |
|-----------|-----------------------------------|
| ML        | scikit-learn, pandas, numpy       |
| Backend   | Flask, Flask-CORS                 |
| Frontend  | HTML5, CSS3, Vanilla JS, Chart.js |
| Reporting | python-docx, matplotlib           |

---

## Dataset

**Seasonal Agriculture Performance Dataset** — 28 features covering:
- Farm metadata (State, District, Crop, Season)
- Environmental conditions (Rainfall, Temperature, Humidity, Sunlight)
- Soil properties (pH, Moisture, NPK)
- Farm management (Irrigation, Fertilizer, Pesticide, Seed Quality)
- Outcome metrics (Yield, Revenue, Profit, Water Efficiency)

**Target variable:** `Yield_Tonnes_Ha`
