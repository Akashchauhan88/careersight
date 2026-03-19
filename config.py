"""
Central configuration for CareerSight.
All paths and constants live here so every module imports from one place.
"""

import os

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DATA_DIR    = os.path.join(BASE_DIR, "data")
MODELS_DIR  = os.path.join(BASE_DIR, "models", "saved")

ROLES_FILE   = os.path.join(DATA_DIR, "roles_master.json")
SKILLS_FILE  = os.path.join(DATA_DIR, "skill_taxonomy.json")
MATRIX_FILE  = os.path.join(DATA_DIR, "role_skill_matrix.csv")
MODEL_FILE   = os.path.join(MODELS_DIR, "rf_model.pkl")
ENCODER_FILE = os.path.join(MODELS_DIR, "label_encoder.pkl")

# ── App meta ───────────────────────────────────────────────────────────────
APP_TITLE   = "CareerSight"
APP_SUBTITLE = "An Explainable AI-Based Career Guidance and Skill Gap Analysis System"
APP_ICON    = "🔭"
APP_VERSION = "1.0"

# ── Scoring ────────────────────────────────────────────────────────────────
MIN_IMPORTANCE_THRESHOLD = 0.4
BAND_EXCELLENT = 80
BAND_GOOD      = 60
BAND_MODERATE  = 40

# ── ML ─────────────────────────────────────────────────────────────────────
RF_N_ESTIMATORS  = 300
RF_MAX_DEPTH     = 12
RF_RANDOM_STATE  = 42
TOP_N_ROLES      = 5
SHAP_MAX_DISPLAY = 10

# ── UI ─────────────────────────────────────────────────────────────────────
CATEGORY_COLORS = {
    "Data & AI":              "#7F77DD",
    "Software Engineering":   "#1D9E75",
    "UX & Design":            "#D85A30",
    "DevOps & Cloud":         "#185FA5",
    "Product & Analytics":    "#BA7517",
}

DEMAND_COLORS = {
    "High":   "#1D9E75",
    "Medium": "#BA7517",
    "Low":    "#E24B4A",
}

SKILL_CATEGORIES = [
    "Technical",
    "Data & Analytics",
    "AI & ML",
    "Design & UX",
    "Infrastructure",
    "Soft Skills",
    "Domain Knowledge",
]