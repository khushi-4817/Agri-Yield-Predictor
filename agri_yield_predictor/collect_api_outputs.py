"""
collect_api_outputs.py
Calls every API endpoint, saves results to reports/api_outputs.json
"""
import json, requests, os

BASE = "http://localhost:5000"
OUT  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports", "api_outputs.json")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

sample_payload = {
    "Crop": "Rice", "Season": "Kharif", "State": "Telangana",
    "District": "Warangal", "Irrigation_Method": "Drip",
    "Farm_Area_Hectares": 5.0, "Rainfall_mm": 700.0,
    "Avg_Temperature_C": 29.0, "Humidity_pct": 70.0,
    "Sunlight_Hours_Day": 7.0, "Soil_pH": 6.2,
    "Soil_Moisture_pct": 28.0, "Nitrogen_kg_ha": 120.0,
    "Phosphorus_kg_ha": 55.0, "Potassium_kg_ha": 110.0,
    "Fertilizer_kg_ha": 180.0, "Pesticide_Litre_ha": 5.0,
    "Seed_Quality_Score": 0.9, "Water_Used_m3": 3000.0,
    "Disease_Pest_Risk_pct": 35.0
}

batch_payload = [
    {**sample_payload, "Crop": "Wheat",  "Rainfall_mm": 400, "Avg_Temperature_C": 22},
    {**sample_payload, "Crop": "Maize",  "Rainfall_mm": 600, "Avg_Temperature_C": 30},
    {**sample_payload, "Crop": "Cotton", "Rainfall_mm": 500, "Avg_Temperature_C": 33},
]

endpoints = [
    ("GET",  "/api/health",          None),
    ("GET",  "/api/meta",            None),
    ("POST", "/api/predict",         sample_payload),
    ("POST", "/api/batch_predict",   batch_payload),
    ("GET",  "/api/stats",           None),
    ("GET",  "/api/model_metrics",   None),
    ("GET",  "/api/crop_analysis",   None),
    ("GET",  "/api/season_analysis", None),
    ("GET",  "/api/state_analysis",  None),
]

outputs = {}
for method, path, body in endpoints:
    url = BASE + path
    try:
        if method == "GET":
            r = requests.get(url, timeout=10)
        else:
            r = requests.post(url, json=body, timeout=10)
        outputs[path] = {"status": r.status_code, "data": r.json()}
        print(f"  {method} {path}  -> {r.status_code}")
    except Exception as e:
        outputs[path] = {"status": "error", "data": str(e)}
        print(f"  {method} {path}  -> ERROR: {e}")

with open(OUT, "w") as f:
    json.dump(outputs, f, indent=2)
print(f"\nSaved -> {OUT}")
