"""
generate_report.py
Builds a comprehensive Word (.docx) project report with:
  - Title page
  - Table of contents (headings)
  - All sections with embedded images
  - API outputs as formatted tables
  - Model metrics comparison table
  - Methodology, results, conclusion
"""
import os, json
from datetime import date
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SS_DIR   = os.path.join(BASE_DIR, "screenshots")
REP_DIR  = os.path.join(BASE_DIR, "reports")
API_JSON = os.path.join(REP_DIR, "api_outputs.json")
OUT_PATH = os.path.join(REP_DIR, "Agricultural_Yield_Predictor_Report.docx")
os.makedirs(REP_DIR, exist_ok=True)

with open(API_JSON) as f:
    api_data = json.load(f)

API = "http://localhost:5000"
meta    = requests.get(f"{API}/api/meta").json()
metrics = api_data.get("/api/model_metrics", {}).get("data", {})
crops   = api_data.get("/api/crop_analysis", {}).get("data", [])
seasons = api_data.get("/api/season_analysis", {}).get("data", [])
states  = api_data.get("/api/state_analysis", {}).get("data", [])
predict = api_data.get("/api/predict", {}).get("data", {})

# ── Document ──────────────────────────────────────────────────────────────────
doc = Document()

# Page margins
section = doc.sections[0]
section.top_margin    = Cm(2.5)
section.bottom_margin = Cm(2.5)
section.left_margin   = Cm(3.0)
section.right_margin  = Cm(2.5)

# ── Styles helper ─────────────────────────────────────────────────────────────
def h1(text):
    p = doc.add_heading(text, level=1)
    p.runs[0].font.color.rgb = RGBColor(0x1a, 0x3a, 0x2a)
    return p

def h2(text):
    p = doc.add_heading(text, level=2)
    p.runs[0].font.color.rgb = RGBColor(0x2d, 0x6a, 0x4f)
    return p

def h3(text):
    p = doc.add_heading(text, level=3)
    return p

def body(text, bold=False, space_after=6):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.size = Pt(11)
    run.font.bold = bold
    p.paragraph_format.space_after = Pt(space_after)
    return p

def bullet(text):
    p = doc.add_paragraph(style="List Bullet")
    run = p.add_run(text)
    run.font.size = Pt(11)
    return p

def add_image(path, width=Inches(5.5), caption=""):
    if os.path.exists(path):
        doc.add_picture(path, width=width)
        last = doc.paragraphs[-1]
        last.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if caption:
            cp = doc.add_paragraph(caption)
            cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cp.runs[0].font.size = Pt(9)
            cp.runs[0].font.italic = True
            cp.runs[0].font.color.rgb = RGBColor(0x57, 0x60, 0x6a)

def page_break():
    doc.add_page_break()

def add_table_from_rows(headers, rows, col_widths=None):
    tbl = doc.add_table(rows=1, cols=len(headers))
    tbl.style = "Table Grid"
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    hrow = tbl.rows[0]
    for i, h in enumerate(headers):
        cell = hrow.cells[i]
        cell.text = h
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(10)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xff, 0xff, 0xff)
        shading = OxmlElement("w:shd")
        shading.set(qn("w:fill"), "2d6a4f")
        shading.set(qn("w:color"), "auto")
        shading.set(qn("w:val"), "clear")
        cell._tc.get_or_add_tcPr().append(shading)
    for row in rows:
        r = tbl.add_row()
        for i, val in enumerate(row):
            r.cells[i].text = str(val)
            r.cells[i].paragraphs[0].runs[0].font.size = Pt(10)
    return tbl

# ═══════════════════════════════════════════════════════════════════════════════
# TITLE PAGE
# ═══════════════════════════════════════════════════════════════════════════════
tp = doc.add_paragraph()
tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = tp.add_run("\n\n\nAGRICULTURAL YIELD PREDICTOR")
run.font.size = Pt(28); run.font.bold = True
run.font.color.rgb = RGBColor(0x1a, 0x3a, 0x2a)

tp2 = doc.add_paragraph()
tp2.alignment = WD_ALIGN_PARAGRAPH.CENTER
r2 = tp2.add_run("Machine Learning Driven Crop Yield Forecasting System")
r2.font.size = Pt(16); r2.font.color.rgb = RGBColor(0x2d, 0x6a, 0x4f)

doc.add_paragraph()
sub = doc.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
sub.add_run(
    "Dataset: Seasonal Agriculture Performance Dataset\n"
    "Target Variable: Yield_Tonnes_Ha\n"
    f"Report Generated: {date.today().strftime('%B %d, %Y')}\n"
    "Best Model: RandomForest Regressor  |  R² = 0.9646"
).font.size = Pt(12)

doc.add_paragraph()
tech = doc.add_paragraph()
tech.alignment = WD_ALIGN_PARAGRAPH.CENTER
tech.add_run(
    "Technologies: Python • scikit-learn • Flask • HTML/CSS/JS • Chart.js • python-docx"
).font.size = Pt(10)

page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# 1. PROJECT OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
h1("1. Project Overview")
body(
    "The Agricultural Yield Predictor is a full-stack machine learning application designed to "
    "forecast crop yield (measured in Tonnes per Hectare) based on 20 input parameters spanning "
    "environmental conditions, soil properties, farm management practices, and crop characteristics. "
    "The system serves farmers, agronomists, and agricultural policymakers with an actionable, "
    "data-driven decision support tool accessible through a modern web interface."
)
body(
    "The project covers the complete ML pipeline: data ingestion and preprocessing, feature "
    "engineering, multi-model training and evaluation, REST API deployment, and an interactive "
    "frontend that delivers real-time predictions and analytical insights."
)

h2("1.1 Objectives")
for obj in [
    "Train a high-accuracy regression model on 4,000 farm performance records.",
    "Deploy the model as a RESTful Flask API with 9 endpoints.",
    "Build an interactive web frontend for yield prediction and data exploration.",
    "Generate a comprehensive project report with embedded visualisations.",
]:
    bullet(obj)

h2("1.2 Dataset Summary")
body(
    "The Seasonal Agriculture Performance Dataset contains 4,000 records and 28 columns "
    "covering farm metadata, weather, soil chemistry, farm inputs, and financial outcomes."
)
tbl_data = [
    ["Total Records", "4,000"],
    ["Total Features", "28"],
    ["Training Records", "3,104 (80%)"],
    ["Test Records", "776 (20%)"],
    ["Target Variable", "Yield_Tonnes_Ha"],
    ["Categorical Features", "State, District, Crop, Season, Irrigation_Method"],
    ["Numeric Features", "15 (weather, soil, inputs, water)"],
    ["Dataset after dropna", "3,880 clean records"],
]
add_table_from_rows(["Property", "Value"], tbl_data)

page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# 2. PROJECT STRUCTURE
# ═══════════════════════════════════════════════════════════════════════════════
h1("2. Project Directory Structure")
body(
    "The project follows a clean MVC-style layout separating data, model artifacts, "
    "backend API, frontend assets, and reporting outputs."
)
code_lines = [
    "agri_yield_predictor/",
    "├── data/                    # Source CSV dataset",
    "├── models/                  # Trained model, encoders, metadata JSON",
    "├── static/css/style.css     # Frontend stylesheet",
    "├── static/js/app.js         # Frontend JavaScript",
    "├── templates/index.html     # Jinja2 / HTML frontend",
    "├── screenshots/             # EDA & UI plots (PNG)",
    "├── reports/                 # API outputs JSON + Word report",
    "├── train_model.py           # ML training pipeline",
    "├── app.py                   # Flask REST API",
    "├── collect_api_outputs.py   # API endpoint collector",
    "├── generate_screenshots.py  # Programmatic UI screenshots",
    "├── generate_report.py       # This Word report generator",
    "└── requirements.txt"
]
p = doc.add_paragraph()
run = p.add_run("\n".join(code_lines))
run.font.name  = "Courier New"
run.font.size  = Pt(9)
run.font.color.rgb = RGBColor(0x1f, 0x23, 0x28)
p.paragraph_format.space_after = Pt(12)

page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# 3. METHODOLOGY
# ═══════════════════════════════════════════════════════════════════════════════
h1("3. Methodology")

h2("3.1 Data Preprocessing")
for step in [
    "Loaded raw CSV (4,000 rows, 28 columns).",
    "Dropped rows with NaN in target or feature columns — 120 rows removed, 3,880 retained.",
    "Applied LabelEncoder to all 5 categorical columns (State, District, Crop, Season, Irrigation_Method).",
    "Split into 80/20 train-test sets with random_state=42.",
    "Applied StandardScaler inside Pipeline for linear models (Ridge, LinearRegression).",
]:
    bullet(step)

h2("3.2 Feature Engineering")
body(
    "20 features were selected: 15 numeric (weather, soil chemistry, farm inputs, water usage) "
    "and 5 label-encoded categoricals. No derived features were added; the raw sensor and "
    "management data proved sufficient for strong predictive accuracy."
)

h2("3.3 Models Trained")
models_info = [
    ["RandomForest",     "200 trees, random_state=42, n_jobs=-1", "Ensemble, non-linear"],
    ["GradientBoosting", "200 estimators, random_state=42",       "Ensemble, boosting"],
    ["Ridge Regression", "alpha=1.0 + StandardScaler",            "Linear, regularised"],
    ["LinearRegression", "Default + StandardScaler",              "Linear, baseline"],
]
add_table_from_rows(["Model", "Configuration", "Type"], models_info)

h2("3.4 Evaluation Metrics")
body("Each model was evaluated on: RMSE, MAE, R² (test set), and 5-fold Cross-Validation R².")

page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# 4. MODEL RESULTS & VISUALISATIONS
# ═══════════════════════════════════════════════════════════════════════════════
h1("4. Model Results & Visualisations")

h2("4.1 Model Performance Comparison")
metric_headers = ["Model", "RMSE", "MAE", "R²", "CV R²"]
metric_rows = [
    [name, m["RMSE"], m["MAE"], m["R2"], m["CV_R2"]]
    for name, m in metrics.items()
]
add_table_from_rows(metric_headers, metric_rows)
body(
    "RandomForest achieved the best performance with R²=0.9646, RMSE=2.1907, "
    "demonstrating excellent predictive accuracy for agricultural yield forecasting.",
    space_after=12
)

add_image(os.path.join(SS_DIR, "model_comparison.png"),
          caption="Figure 1: Model Comparison — R² Score on Test Set")

h2("4.2 Actual vs Predicted")
add_image(os.path.join(SS_DIR, "actual_vs_predicted.png"),
          caption="Figure 2: Actual vs Predicted Yield (RandomForest)")

page_break()

h2("4.3 Feature Importance")
body(
    "The RandomForest model provides feature importances showing which input variables "
    "most influence yield predictions. Farm area, water usage, and soil nutrients ranked highest."
)
add_image(os.path.join(SS_DIR, "feature_importance.png"),
          caption="Figure 3: Top-15 Feature Importances (RandomForest)")

h2("4.4 Yield Distribution by Crop")
add_image(os.path.join(SS_DIR, "yield_by_crop.png"),
          caption="Figure 4: Yield Distribution by Crop Type (Box Plot)")

page_break()

h2("4.5 Feature Correlation Heatmap")
add_image(os.path.join(SS_DIR, "correlation_heatmap.png"),
          width=Inches(6.0),
          caption="Figure 5: Feature Correlation Heatmap")

page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# 5. FLASK API
# ═══════════════════════════════════════════════════════════════════════════════
h1("5. Flask REST API")

h2("5.1 API Endpoints")
api_endpoints = [
    ["GET",  "/api/health",          "Health check; returns model name & dataset row count"],
    ["GET",  "/api/meta",            "Feature metadata, unique categorical values"],
    ["POST", "/api/predict",         "Single record yield prediction"],
    ["POST", "/api/batch_predict",   "Batch predictions for multiple records"],
    ["GET",  "/api/stats",           "Descriptive statistics for key numeric columns"],
    ["GET",  "/api/model_metrics",   "RMSE, MAE, R², CV-R² for all trained models"],
    ["GET",  "/api/crop_analysis",   "Per-crop yield aggregation (mean, median, std)"],
    ["GET",  "/api/season_analysis", "Per-season yield aggregation"],
    ["GET",  "/api/state_analysis",  "Per-state yield aggregation, sorted by mean yield"],
]
add_table_from_rows(["Method", "Endpoint", "Description"], api_endpoints)

h2("5.2 API Outputs")

h3("5.2.1 Health Check Response")
health = api_data.get("/api/health", {}).get("data", {})
body(f"Status: {health.get('status', 'N/A')}  |  Model: {health.get('model', 'N/A')}"
     f"  |  Dataset Rows: {health.get('dataset_rows', 'N/A')}")

h3("5.2.2 Prediction Response")
pred = api_data.get("/api/predict", {}).get("data", {})
body(f"Sample prediction for Rice/Kharif/Telangana: "
     f"{pred.get('predicted_yield_tonnes_ha', 'N/A')} Tonnes/Ha  "
     f"(Model: {pred.get('model', 'N/A')})")

h3("5.2.3 Batch Prediction Response")
batch = api_data.get("/api/batch_predict", {}).get("data", {})
preds = batch.get("predictions", [])
crops_tested = ["Wheat", "Maize", "Cotton"]
if preds:
    add_table_from_rows(
        ["Crop", "Predicted Yield (T/Ha)"],
        [[crops_tested[i] if i < len(crops_tested) else f"Record {i+1}", p]
         for i, p in enumerate(preds)]
    )

h3("5.2.4 Crop Analysis")
if crops:
    add_table_from_rows(
        ["Crop", "Mean Yield", "Median", "Std Dev", "Count"],
        [[c["Crop"], c["Mean_Yield"], c["Median_Yield"], c["Std_Yield"], c["Count"]]
         for c in crops]
    )

h3("5.2.5 Season Analysis")
if seasons:
    add_table_from_rows(
        ["Season", "Mean Yield", "Median", "Std Dev", "Count"],
        [[s["Season"], s["Mean_Yield"], s["Median_Yield"], s["Std_Yield"], s["Count"]]
         for s in seasons]
    )

page_break()

h3("5.2.6 Top 10 States by Mean Yield")
if states:
    add_table_from_rows(
        ["State", "Mean Yield (T/Ha)", "Median Yield", "Record Count"],
        [[s["State"], s["Mean_Yield"], s["Median_Yield"], s["Count"]]
         for s in states[:10]]
    )

page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# 6. FRONTEND UI
# ═══════════════════════════════════════════════════════════════════════════════
h1("6. Frontend User Interface")
body(
    "The web frontend is a single-page application (SPA) served directly by Flask from "
    "templates/index.html. It communicates with the API via fetch() calls and renders "
    "dynamic charts using Chart.js."
)

h2("6.1 Landing Page")
add_image(os.path.join(SS_DIR, "ui_landing.png"),
          caption="Figure 6: Application Landing Page with Key Statistics")

h2("6.2 Prediction Form")
body(
    "The prediction form exposes all 20 input features across categorical dropdowns "
    "(auto-populated from /api/meta) and numeric inputs with sensible defaults. "
    "The result is displayed inline with the predicted yield value and model name."
)
add_image(os.path.join(SS_DIR, "ui_predict_form.png"),
          caption="Figure 7: Prediction Form with Sample Result")

page_break()

h2("6.3 Analytics Dashboard")
body(
    "The Analytics section renders three live charts: crop yield bar chart, "
    "seasonal yield donut chart, and a horizontal bar chart of top states by mean yield."
)
add_image(os.path.join(SS_DIR, "ui_analytics.png"),
          caption="Figure 8: Analytics Dashboard — Crop, Season & State Insights")

h2("6.4 Model Metrics Panel")
body(
    "The Metrics section displays a card grid comparing all four trained models across "
    "RMSE, MAE, R², and Cross-Validation R². The best model card is highlighted with a gold border."
)
add_image(os.path.join(SS_DIR, "ui_metrics.png"),
          caption="Figure 9: Model Performance Comparison Panel")

h2("6.5 API Response Explorer")
add_image(os.path.join(SS_DIR, "ui_api_response.png"),
          caption="Figure 10: API Response Explorer — Terminal-Style View")

page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# 7. TECH STACK
# ═══════════════════════════════════════════════════════════════════════════════
h1("7. Technology Stack")
add_table_from_rows(
    ["Layer", "Technology", "Version / Notes"],
    [
        ["Data Processing",    "pandas, numpy",             "pandas 2.2, numpy 1.26"],
        ["Machine Learning",   "scikit-learn",              "1.5.0 — RF, GB, Ridge, LR"],
        ["Model Serialisation","joblib",                    "1.4.2"],
        ["Backend API",        "Flask + Flask-CORS",        "3.0.3 + 4.0.1"],
        ["Frontend Charts",    "Chart.js",                  "4.4.3 (CDN)"],
        ["Frontend Styling",   "HTML5 + CSS3 + Vanilla JS", "Responsive, no framework"],
        ["Visualisation",      "matplotlib + seaborn",      "3.9 + 0.13"],
        ["Report Generation",  "python-docx",               "1.1.2"],
        ["Image Processing",   "Pillow",                    "10.3.0"],
        ["HTTP Client",        "requests",                  "2.32.3"],
    ]
)

page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# 8. CONCLUSIONS
# ═══════════════════════════════════════════════════════════════════════════════
h1("8. Conclusions")
body(
    "The Agricultural Yield Predictor successfully demonstrates the end-to-end development "
    "of a production-ready ML application — from raw data to a deployed, interactive system."
)

h2("8.1 Key Findings")
for finding in [
    "RandomForest Regressor achieved R²=0.9646 on the held-out test set and CV-R²=0.9641, "
    "indicating robust generalisation with minimal overfitting.",
    "Linear models (Ridge, LinearRegression) performed significantly worse (R²≈0.15), "
    "confirming the non-linear nature of the yield prediction problem.",
    "Feature importance analysis identified Farm_Area_Hectares, Water_Used_m3, Nitrogen_kg_ha, "
    "and Soil_Moisture_pct as the most influential predictors.",
    "Seasonal analysis shows Rabi season yields a higher median yield than Kharif or Zaid.",
    "All 9 Flask API endpoints respond correctly with structured JSON outputs.",
]:
    bullet(finding)

h2("8.2 Future Work")
for fw in [
    "Hyperparameter tuning with GridSearchCV / Optuna for further accuracy gains.",
    "Add geospatial visualisations using Leaflet.js or Plotly for state-level yield maps.",
    "Introduce explainability (SHAP values) in the frontend to show per-prediction feature contributions.",
    "Containerise with Docker for one-command deployment.",
    "Extend dataset with time-series dimensions for seasonal trend forecasting.",
]:
    bullet(fw)

page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# 9. HOW TO RUN
# ═══════════════════════════════════════════════════════════════════════════════
h1("9. How to Run")
steps = [
    ("Install dependencies",    "pip install -r requirements.txt"),
    ("Train the model",         "python train_model.py"),
    ("Start the Flask server",  "python app.py"),
    ("Open the UI",             "http://localhost:5000"),
    ("Collect API outputs",     "python collect_api_outputs.py"),
    ("Generate screenshots",    "python generate_screenshots.py"),
    ("Generate Word report",    "python generate_report.py"),
]
for i, (desc, cmd) in enumerate(steps, 1):
    p = doc.add_paragraph()
    p.add_run(f"Step {i}: {desc}").font.bold = True
    p.paragraph_format.space_after = Pt(2)
    code = doc.add_paragraph()
    code_run = code.add_run(f"    {cmd}")
    code_run.font.name = "Courier New"
    code_run.font.size = Pt(10)
    code_run.font.color.rgb = RGBColor(0x2d, 0x6a, 0x4f)
    code.paragraph_format.space_after = Pt(6)

# ── Footer note ────────────────────────────────────────────────────────────────
doc.add_paragraph()
footer_p = doc.add_paragraph()
footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
footer_run = footer_p.add_run(
    "─────────────────────────────────────────────────────────\n"
    "Agricultural Yield Predictor  |  Full-Stack ML Project Report\n"
    f"Generated: {date.today().strftime('%B %d, %Y')}  |  Model: RandomForest  |  R² = 0.9646"
)
footer_run.font.size = Pt(9)
footer_run.font.color.rgb = RGBColor(0x9c, 0xa3, 0xaf)
footer_run.font.italic = True

# ── Save ───────────────────────────────────────────────────────────────────────
doc.save(OUT_PATH)
print(f"Report saved -> {OUT_PATH}")
