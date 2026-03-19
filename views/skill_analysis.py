"""Skill Gap Analysis Page — persistent state, no default role."""

import streamlit as st
from engine.data_loader import load_roles, get_skills_for_role
from engine.skill_matcher import compute_compatibility, get_skill_vectors
from components.radar_chart import render_radar_chart
from components.skill_bars import render_skill_bars, render_gap_bars
from utils.helpers import score_to_band, format_salary, format_growth
from config import MIN_IMPORTANCE_THRESHOLD


def _init_state():
    if "sa_user_skills"  not in st.session_state: st.session_state["sa_user_skills"]  = {}
    if "sa_results"      not in st.session_state: st.session_state["sa_results"]      = None
    if "sa_role_id"      not in st.session_state: st.session_state["sa_role_id"]      = None
    if "sa_role_title"   not in st.session_state: st.session_state["sa_role_title"]   = None
    if "sa_cat_filter"   not in st.session_state: st.session_state["sa_cat_filter"]   = "All"
    if "sa_selected"     not in st.session_state: st.session_state["sa_selected"]     = False


def _build_skill_sliders(role_id):
    role_skills = get_skills_for_role(role_id)
    role_skills = role_skills[role_skills["importance_score"] >= MIN_IMPORTANCE_THRESHOLD]
    user_skills = {}
    for cat in role_skills["category"].unique():
        cat_skills = role_skills[role_skills["category"] == cat]
        st.markdown(f"**{cat}**")
        for _, row in cat_skills.iterrows():
            sid     = row["skill_id"]
            default = float(st.session_state["sa_user_skills"].get(sid, 0.0))
            val = st.slider(
                f"{row['skill_name']}  _(required: {row['importance_score']:.1f})_",
                0.0, 1.0, default, 0.05,
                key  = f"sa_slider_{role_id}_{sid}",
                help = f"Required level: **{row['level_required']}**",
            )
            user_skills[sid] = val
        st.markdown("")
    return user_skills


def render():
    _init_state()

    st.markdown("## Skill Gap Analysis")
    st.markdown("Select a target role, rate your skills, and see your compatibility score.")
    st.divider()

    roles    = sorted(load_roles(), key=lambda r: r["title"])
    role_map = {r["title"]: r for r in roles}

    col_role, col_cat = st.columns([3, 2])
    with col_cat:
        all_cats = ["All"] + sorted({r["category"] for r in roles})
        prev_cat = st.session_state["sa_cat_filter"]
        cat_idx  = all_cats.index(prev_cat) if prev_cat in all_cats else 0
        sel_cat  = st.selectbox("Filter by category", all_cats, index=cat_idx, key="sa_cat")
        st.session_state["sa_cat_filter"] = sel_cat

    with col_role:
        filtered = roles if sel_cat == "All" else [r for r in roles if r["category"] == sel_cat]
        titles   = [r["title"] for r in filtered]
        options  = ["— Select a role —"] + titles

        prev_title = st.session_state["sa_role_title"]
        def_idx    = options.index(prev_title) if prev_title in options else 0
        sel_title  = st.selectbox("Select target role", options, index=def_idx, key="sa_role")

    # Show placeholder if no role selected
    if sel_title == "— Select a role —":
        st.info("Select a target role from the dropdown above to begin your skill analysis.")
        return

    role = role_map[sel_title]

    # Quick stats
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Salary", format_salary(role["salary_range"]))
    c2.metric("📈 Growth",  format_growth(role.get("growth_rate", 0)))
    c3.metric("📣 Demand",  role["demand_level"])
    st.divider()

    # Reset if role changed
    if st.session_state["sa_role_id"] != role["role_id"]:
        st.session_state["sa_user_skills"] = {}
        st.session_state["sa_results"]     = None
        st.session_state["sa_role_id"]     = role["role_id"]
        st.session_state["sa_role_title"]  = sel_title
        st.session_state["sa_selected"]    = True

    st.markdown("### Rate your current skill levels")
    st.caption("0.0 = No knowledge · 0.5 = Working knowledge · 1.0 = Expert")

    with st.form("skill_form"):
        user_skills = _build_skill_sliders(role["role_id"])
        submitted   = st.form_submit_button("Calculate My Compatibility", use_container_width=True)

    if submitted:
        st.session_state["sa_user_skills"]   = user_skills
        st.session_state["sa_role_title"]    = sel_title
        result = compute_compatibility(user_skills, role["role_id"])
        st.session_state["sa_results"]       = result
        st.session_state["last_user_skills"] = user_skills
        st.session_state["last_role_id"]     = role["role_id"]
        st.session_state["last_role_title"]  = sel_title

    result = st.session_state.get("sa_results")
    if not result:
        st.info("Rate your skills above and click **Calculate My Compatibility** to see results.")
        return

    score       = result["score"]
    band, color = score_to_band(score)

    st.divider()
    st.markdown("### Your Results")

    col_score, col_info = st.columns([1, 2])
    with col_score:
        st.markdown(
            f"<div style='text-align:center;padding:24px;border:2px solid {color};"
            f"border-radius:16px;background:{color}18'>"
            f"<div style='font-size:52px;font-weight:700;color:{color}'>{score:.1f}%</div>"
            f"<div style='font-size:16px;color:{color};margin-top:4px'>{band}</div>"
            f"</div>", unsafe_allow_html=True,
        )
    with col_info:
        st.markdown(f"""
**Role:** {st.session_state['sa_role_title']}

✅ **{len(result['strengths'])} skills** meet or exceed the requirement

🔴 **{len(result['gaps'])} skills** need improvement
""")

    st.divider()
    st.markdown("### Skill Profile Radar")
    saved = st.session_state["sa_user_skills"]
    skill_names, role_vec, user_vec = get_skill_vectors(role["role_id"], saved)
    render_radar_chart(skill_names, role_vec, user_vec,
                       role_title=st.session_state["sa_role_title"])

    st.divider()
    tab_all, tab_str, tab_gap = st.tabs(["All Skills", "Strengths", "Gaps"])
    with tab_all:
        render_skill_bars(result["skill_details"],
                          title=f"Your Skills vs {st.session_state['sa_role_title']}")
    with tab_str:
        if result["strengths"]:
            for s in result["strengths"]:
                st.markdown(
                    f"✅ **{s['skill_name']}** — "
                    f"You: `{s['user_level']:.2f}` · Required: `{s['importance']:.2f}` · "
                    f"Surplus: `+{s['user_level']-s['importance']:.2f}`")
        else:
            st.info("No skills fully meet the requirement yet.")
    with tab_gap:
        render_gap_bars(result["gaps"])
        if result["gaps"]:
            st.markdown("#### Priority skills to improve:")
            for i, g in enumerate(result["gaps"][:5], 1):
                st.markdown(f"{i}. **{g['skill_name']}** — Gap: `{g['gap']:.2f}` · {g['level_required']}")

    st.caption("Your profile is saved — open Learning Path Generator or Export Report to continue.")