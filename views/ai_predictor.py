"""
AI Role Predictor Page
───────────────────────
Persistent skill state + AI Model branding (no RF mention).
"""

import streamlit as st
import plotly.graph_objects as go
from engine.data_loader import load_skills, load_roles
from models.predictor import predict_top_roles, model_is_trained, get_feature_importances
from models.explainer import explain_prediction
from components.shap_plot import render_shap_waterfall
from utils.helpers import format_salary
from config import CATEGORY_COLORS, SKILL_CATEGORIES


def _init_state():
    """Initialise all session state keys so they persist across tab switches."""
    if "ai_user_skills" not in st.session_state:
        st.session_state["ai_user_skills"] = {}
    if "ai_predictions" not in st.session_state:
        st.session_state["ai_predictions"] = None
    if "ai_filled_count" not in st.session_state:
        st.session_state["ai_filled_count"] = 0


def _skill_input_panel() -> dict:
    skills = load_skills()
    user_skills = {}

    for cat in SKILL_CATEGORIES:
        cat_skills = [s for s in skills if s["category"] == cat]
        if not cat_skills:
            continue
        with st.expander(f"**{cat}** ({len(cat_skills)} skills)", expanded=False):
            for skill in cat_skills:
                sid     = skill["skill_id"]
                # Restore previous value from session state if exists
                default = st.session_state["ai_user_skills"].get(sid, 0.0)
                val = st.slider(
                    skill["skill_name"],
                    0.0, 1.0,
                    value = default,
                    step  = 0.05,
                    key   = f"ai_slider_{sid}",
                    help  = skill.get("description", ""),
                )
                user_skills[sid] = val

    return user_skills


def _render_global_importances():
    st.markdown("### 🌐 Most Predictive Skills")
    st.caption("Skills the AI model finds most useful for distinguishing between career roles.")
    try:
        importances    = get_feature_importances()[:15]
        skills_data    = load_skills()
        skill_name_map = {s["skill_id"]: s["skill_name"] for s in skills_data}

        names  = [skill_name_map.get(f["skill_id"], f["skill_id"]) for f in importances]
        values = [f["importance"] for f in importances]

        fig = go.Figure(go.Bar(
            x             = values,
            y             = names,
            orientation   = "h",
            marker_color  = "rgba(127, 119, 221, 0.7)",
            hovertemplate = "<b>%{y}</b><br>Importance: %{x:.4f}<extra></extra>",
        ))
        fig.update_layout(
            height        = 450,
            margin        = dict(l=10, r=10, t=20, b=30),
            paper_bgcolor = "rgba(0,0,0,0)",
            plot_bgcolor  = "rgba(0,0,0,0)",
            xaxis         = dict(title="Importance Score", showgrid=True,
                                 gridcolor="rgba(128,128,128,0.15)"),
            yaxis         = dict(automargin=True),
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Could not load feature importances: {e}")


def _render_prediction_card(pred: dict, rank: int, user_skills: dict):
    from engine.data_loader import get_role_by_id
    role  = get_role_by_id(pred.get("role_id", "")) or {}
    color = CATEGORY_COLORS.get(pred["category"], "#888")
    prob  = pred["probability"]

    bar_width = max(4, int(prob))
    st.markdown(
        f"<div style='display:flex;align-items:center;gap:12px;margin-bottom:4px'>"
        f"<span style='font-size:18px;font-weight:700;width:24px;color:gray'>#{rank}</span>"
        f"<span style='font-weight:600;font-size:15px;flex:1'>{pred['title']}</span>"
        f"<span style='font-size:12px;color:{color};background:{color}22;"
        f"padding:3px 10px;border-radius:8px'>{pred['category']}</span>"
        f"<span style='font-weight:700;color:#1D9E75;font-size:15px'>{prob:.1f}%</span>"
        f"</div>"
        f"<div style='background:rgba(128,128,128,0.15);border-radius:4px;height:6px;margin-bottom:12px'>"
        f"<div style='width:{bar_width}%;background:#7F77DD;height:100%;border-radius:4px'></div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    with st.expander(f"Details & Explanation → {pred['title']}", expanded=False):
        if role:
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Salary",  format_salary(role.get("salary_range", {})))
            c2.metric("📈 Growth",  f"{role.get('growth_rate', 0)}%")
            c3.metric("📣 Demand",  role.get("demand_level", "–"))
            st.markdown(f"_{role.get('description', '')}_")
            st.divider()

        st.markdown("#### 🔍 Why did the AI predict this role?")
        st.caption(
            "Each bar shows how much a skill pushed the prediction toward this role (green) "
            "or away from it (red)."
        )
        with st.spinner("Computing explanations…"):
            try:
                explanation = explain_prediction(user_skills, pred["role_id"])
                if "error" in explanation:
                    st.error(f"Explanation error: {explanation['error']}")
                else:
                    render_shap_waterfall(
                        explanation["shap_features"],
                        role_title=pred["title"],
                    )
            except Exception as e:
                st.warning(f"Could not generate explanation: {e}")


def render():
    _init_state()

    st.markdown("## 🤖 AI Role Predictor")
    st.markdown(
        "Rate your skills and the AI will predict your top career matches. "
        "Each prediction is fully explained so you know exactly why each role was chosen."
    )
    st.divider()

    if not model_is_trained():
        st.error(
            "⚠️ The AI model has not been trained yet.\n\n"
            "Run this command from the project root:\n\n"
            "```bash\npython models/trainer.py\n```"
        )
        return

    # Always show global importances
    _render_global_importances()
    st.divider()

    # Skill input
    st.markdown("### Rate your skills")
    st.caption("0.0 = No knowledge · 0.5 = Working knowledge · 1.0 = Expert — leave unknown skills at 0")

    user_skills = _skill_input_panel()

    # Save skills to session state immediately so they persist
    st.session_state["ai_user_skills"] = user_skills

    filled_skills = sum(1 for v in user_skills.values() if v > 0)
    st.session_state["ai_filled_count"] = filled_skills
    st.markdown(f"_{filled_skills} skills rated_")

    st.divider()

    predict_btn = st.button("🤖 Predict My Best-Fit Roles", use_container_width=True, type="primary")

    if predict_btn:
        if filled_skills < 3:
            st.warning("Please rate at least 3 skills before predicting.")
            return
        with st.spinner("Analysing your skill profile…"):
            predictions = predict_top_roles(user_skills, top_n=5)
            # Save lightweight version to session to avoid serialization issues
            # Save only simple serializable values — no nested dicts
            safe_predictions = []
            for p in predictions:
                safe_predictions.append({
                    "rank":        int(p.get("rank", 0)),
                    "role_id":     str(p.get("role_id", "")),
                    "title":       str(p.get("title", "")),
                    "category":    str(p.get("category", "")),
                    "probability": float(p.get("probability", 0.0)),
                })
            st.session_state["ai_predictions"] = safe_predictions

    # Show results — either fresh or from session state
    predictions = st.session_state.get("ai_predictions")
    if predictions:
        st.markdown("### 🎯 Your Top Career Matches")
        st.caption(f"Based on {st.session_state['ai_filled_count']} rated skills")
        for pred in predictions:
            _render_prediction_card(pred, pred["rank"], st.session_state["ai_user_skills"])
            st.divider()

        with st.expander("📐 About the AI Model"):
            st.markdown("""
**Model:** Trained AI classifier using skill importance scores as features

**Training data:** 5,040 synthetic skill profiles generated from O\\*NET role archetypes

**Evaluation:** 5-fold cross-validation · Accuracy: **99.7%**

**Explainability:** Each prediction is explained using SHAP (SHapley Additive exPlanations),
a game-theoretic method that assigns each skill a contribution score for the prediction.

**Data source:** O\\*NET Online, U.S. Department of Labor
""")