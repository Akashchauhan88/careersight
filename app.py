"""CareerSight — Main Entry Point. Run with: streamlit run app.py"""

import streamlit as st
from config import APP_TITLE, APP_ICON, APP_SUBTITLE
from utils.constants import (
    PAGE_HOME, PAGE_EXPLORER, PAGE_ANALYSIS,
    PAGE_WHATIF, PAGE_PREDICTOR, PAGE_COMPARISON,
    PAGE_TRANSITION, PAGE_LEARNING, PAGE_EXPORT, PAGES,
)

st.set_page_config(
    page_title            = APP_TITLE,
    page_icon             = APP_ICON,
    layout                = "wide",
    initial_sidebar_state = "expanded",
)

# Auto-train model if not exists (needed for fresh deployments)
import os
from config import MODEL_FILE, ENCODER_FILE, MODELS_DIR

if not os.path.exists(MODEL_FILE) or not os.path.exists(ENCODER_FILE):
    with st.spinner("Setting up AI model for first time... This takes about 30 seconds."):
        try:
            import sys
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            os.makedirs(MODELS_DIR, exist_ok=True)
            from models.trainer import train_and_save
            train_and_save()
            st.success("AI model ready!")
            st.rerun()
        except Exception as e:
            st.error(f"Model setup failed: {e}")
            st.stop()

st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── Hide default Streamlit elements ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.8rem 2.5rem 2rem 2.5rem !important; max-width: 1200px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #0f1724 100%) !important;
    border-right: 1px solid #1e2d3d !important;
    min-width: 250px !important;
}
[data-testid="stSidebar"] .stRadio label {
    font-size: 13.5px !important;
    font-weight: 400 !important;
    color: #8b9ab0 !important;
    padding: 6px 12px !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
    display: block !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    color: #e2e8f0 !important;
    background: rgba(127,119,221,0.1) !important;
}
[data-testid="stSidebar"] .stRadio [data-checked="true"] label,
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:has(input:checked) {
    color: #a78bfa !important;
    background: rgba(127,119,221,0.15) !important;
    font-weight: 500 !important;
}

/* ── Main background ── */
.stApp {
    background: #0d1117 !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: #0f1724 !important;
    border: 1px solid #1e2d3d !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
}
[data-testid="stMetricLabel"] {
    font-size: 12px !important;
    color: #8b9ab0 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.4rem !important;
    font-weight: 600 !important;
    color: #e2e8f0 !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #7F77DD 0%, #6366f1 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    padding: 10px 20px !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 12px rgba(127,119,221,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 16px rgba(127,119,221,0.4) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Download button ── */
.stDownloadButton > button {
    background: linear-gradient(135deg, #1D9E75 0%, #059669 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    padding: 10px 20px !important;
    box-shadow: 0 4px 12px rgba(29,158,117,0.3) !important;
    transition: all 0.2s ease !important;
}
.stDownloadButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 16px rgba(29,158,117,0.4) !important;
}

/* ── Sliders ── */
.stSlider [data-baseweb="slider"] {
    padding: 4px 0 !important;
}
.stSlider [data-baseweb="slider"] [role="slider"] {
    background: #7F77DD !important;
    border: 2px solid #a78bfa !important;
}

/* ── Selectbox ── */
.stSelectbox [data-baseweb="select"] {
    background: #0f1724 !important;
    border: 1px solid #1e2d3d !important;
    border-radius: 10px !important;
}

/* ── Text input ── */
.stTextInput input {
    background: #0f1724 !important;
    border: 1px solid #1e2d3d !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-size: 14px !important;
}
.stTextInput input:focus {
    border-color: #7F77DD !important;
    box-shadow: 0 0 0 2px rgba(127,119,221,0.2) !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #0f1724 !important;
    border: 1px solid #1e2d3d !important;
    border-radius: 12px !important;
    margin-bottom: 8px !important;
}
[data-testid="stExpander"]:hover {
    border-color: #2d3f55 !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #0f1724 !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid #1e2d3d !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    color: #8b9ab0 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 8px 16px !important;
    transition: all 0.2s ease !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #7F77DD 0%, #6366f1 100%) !important;
    color: white !important;
}

/* ── Divider ── */
hr {
    border: none !important;
    border-top: 1px solid #1e2d3d !important;
    margin: 1.5rem 0 !important;
}

/* ── Success / Info / Warning / Error ── */
.stSuccess {
    background: rgba(29,158,117,0.1) !important;
    border: 1px solid rgba(29,158,117,0.3) !important;
    border-radius: 10px !important;
    color: #34d399 !important;
}
.stInfo {
    background: rgba(99,102,241,0.1) !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    border-radius: 10px !important;
    color: #818cf8 !important;
}
.stWarning {
    background: rgba(186,117,23,0.1) !important;
    border: 1px solid rgba(186,117,23,0.3) !important;
    border-radius: 10px !important;
}
.stError {
    background: rgba(226,75,74,0.1) !important;
    border: 1px solid rgba(226,75,74,0.3) !important;
    border-radius: 10px !important;
}

/* ── Multiselect ── */
[data-baseweb="tag"] {
    background: rgba(127,119,221,0.2) !important;
    border: 1px solid rgba(127,119,221,0.4) !important;
    border-radius: 6px !important;
    color: #a78bfa !important;
}

/* ── Radio buttons ── */
.stRadio [data-baseweb="radio"] {
    gap: 8px !important;
}

/* ── Form ── */
[data-testid="stForm"] {
    background: #0f1724 !important;
    border: 1px solid #1e2d3d !important;
    border-radius: 14px !important;
    padding: 20px !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0d1117; }
::-webkit-scrollbar-thumb { background: #1e2d3d; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #2d3f55; }

/* ── Caption ── */
.stCaption { color: #8b9ab0 !important; font-size: 12px !important; }

/* ── Headings ── */
h1 { color: #e2e8f0 !important; font-weight: 700 !important; letter-spacing: -0.02em !important; }
h2 { color: #e2e8f0 !important; font-weight: 600 !important; }
h3 { color: #cbd5e1 !important; font-weight: 600 !important; }

/* ── Spinner ── */
.stSpinner { color: #7F77DD !important; }

/* ── Sidebar app name ── */
.sidebar-brand {
    padding: 8px 0 16px 0;
    border-bottom: 1px solid #1e2d3d;
    margin-bottom: 16px;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand
    st.markdown(
        f"<div style='padding:16px 0 20px 0;border-bottom:1px solid #1e2d3d;margin-bottom:12px'>"
        f"<div style='font-size:20px;font-weight:700;color:#e2e8f0;letter-spacing:-0.02em'>"
        f"{APP_ICON} {APP_TITLE}</div>"
        f"<div style='font-size:10px;color:#64748b;margin-top:4px;line-height:1.4'>"
        f"Explainable AI Career Guidance</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Navigation label
    st.markdown(
        "<div style='font-size:10px;color:#64748b;text-transform:uppercase;"
        "letter-spacing:0.08em;font-weight:600;margin-bottom:6px;padding:0 4px'>"
        "Navigation</div>",
        unsafe_allow_html=True,
    )

    # Page groups with dividers
    page_groups = [
        ("Explore", [PAGE_HOME, PAGE_EXPLORER]),
        ("Analyse", [PAGE_ANALYSIS, PAGE_WHATIF, PAGE_PREDICTOR]),
        ("Compare & Plan", [PAGE_COMPARISON, PAGE_TRANSITION, PAGE_LEARNING]),
        ("Export", [PAGE_EXPORT]),
    ]

    page = None
    for group_name, group_pages in page_groups:
        st.markdown(
            f"<div style='font-size:10px;color:#4a5568;text-transform:uppercase;"
            f"letter-spacing:0.06em;padding:8px 4px 4px;font-weight:500'>{group_name}</div>",
            unsafe_allow_html=True,
        )
        for p in group_pages:
            selected = st.session_state.get("_nav_page", PAGE_HOME) == p
            if st.button(
                p,
                key=f"nav_{p}",
                use_container_width=True,
            ):
                st.session_state["_nav_page"] = p
                st.rerun()

    # Read current page
    if "_nav_page" not in st.session_state:
        st.session_state["_nav_page"] = PAGE_HOME
    page = st.session_state["_nav_page"]

    # Session status
    st.markdown(
        "<div style='margin-top:20px;padding-top:16px;border-top:1px solid #1e2d3d'>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='font-size:10px;color:#64748b;text-transform:uppercase;"
        "letter-spacing:0.08em;font-weight:600;margin-bottom:8px'>Progress</div>",
        unsafe_allow_html=True,
    )

    has_analysis   = bool(st.session_state.get("last_role_title"))
    has_ai         = bool(st.session_state.get("ai_predictions"))
    has_lp         = bool(st.session_state.get("lp_generated"))
    has_transition = bool(st.session_state.get("ct_result"))

    items = [
        ("Skill Analysis",  has_analysis),
        ("AI Prediction",   has_ai),
        ("Learning Path",   has_lp),
        ("Transition Plan", has_transition),
    ]
    for label, done in items:
        dot_color = "#1D9E75" if done else "#1e2d3d"
        text_color = "#8b9ab0" if done else "#4a5568"
        st.markdown(
            f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:6px'>"
            f"<span style='width:7px;height:7px;border-radius:50%;background:{dot_color};"
            f"display:inline-block;flex-shrink:0'></span>"
            f"<span style='font-size:12px;color:{text_color}'>{label}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

# ── Page routing ───────────────────────────────────────────────────────────
if page == PAGE_HOME:
    from views.home import render
elif page == PAGE_EXPLORER:
    from views.role_explorer import render
elif page == PAGE_ANALYSIS:
    from views.skill_analysis import render
elif page == PAGE_WHATIF:
    from views.whatif import render
elif page == PAGE_PREDICTOR:
    from views.ai_predictor import render
elif page == PAGE_COMPARISON:
    from views.comparison import render
elif page == PAGE_TRANSITION:
    from views.career_transition import render
elif page == PAGE_LEARNING:
    from views.learning_path import render
elif page == PAGE_EXPORT:
    from views.export_report import render

render()