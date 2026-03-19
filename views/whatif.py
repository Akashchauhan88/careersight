"""
What-If Simulator Page
───────────────────────
Users boost specific skills and see the before/after score change
with side-by-side radar charts.
"""

import streamlit as st
from engine.data_loader import load_roles, get_skills_for_role
from engine.simulator import simulate_improvement, recommend_top_improvements
from engine.skill_matcher import compute_compatibility, get_skill_vectors
from components.radar_chart import render_radar_chart
from utils.helpers import score_to_band
from config import MIN_IMPORTANCE_THRESHOLD


def render():
    st.markdown("## 🔮 What-If Skill Simulator")
    st.markdown(
        "Simulate improving your skills and see **instantly** how your compatibility score changes. "
        "Great for deciding what to learn next."
    )
    st.divider()

    roles    = sorted(load_roles(), key=lambda r: r["title"])
    role_map = {r["title"]: r["role_id"] for r in roles}
    id_map   = {r["role_id"]: r for r in roles}

    # ── Role selection ─────────────────────────────────────────────────────
    # Pre-fill from Skill Analysis page if available
    last_title = st.session_state.get("last_role_title", roles[0]["title"])
    default_idx = list(role_map.keys()).index(last_title) if last_title in role_map else 0

    options   = ["— Select a role —"] + list(role_map.keys())
    def_idx_p = default_idx + 1 if default_idx >= 0 else 0
    sel_title = st.selectbox(
        "Select target role",
        options,
        index=def_idx_p,
        key="wi_role",
    )
    if sel_title == "— Select a role —":
        st.info("Select a target role above to begin the simulation.")
        return
    role_id   = role_map[sel_title]
    role      = id_map[role_id]
    st.session_state["wi_role_id"]    = role_id
    st.session_state["wi_role_title"] = sel_title

    # ── Base skill input ───────────────────────────────────────────────────
    role_skills = get_skills_for_role(role_id)
    role_skills = role_skills[role_skills["importance_score"] >= MIN_IMPORTANCE_THRESHOLD]

    # Use saved skills if available and same role
    saved_skills = st.session_state.get("last_user_skills", {})
    saved_role   = st.session_state.get("last_role_id", "")

    st.markdown("### Step 1 — Set your current skill levels")
    if saved_skills and saved_role == role_id:
        st.success("✅ Loaded your skill profile from the Skill Analysis page.")
        use_saved = st.checkbox("Use my saved skill profile", value=True, key="wi_use_saved")
    else:
        use_saved = False

    base_skills = {}
    with st.expander("📝 Edit base skill levels", expanded=not use_saved):
        for _, row in role_skills.iterrows():
            sid       = row["skill_id"]
            default   = saved_skills.get(sid, 0.0) if use_saved else 0.0
            base_skills[sid] = st.slider(
                f"{row['skill_name']}",
                0.0, 1.0,
                value   = float(default),
                step    = 0.05,
                key     = f"wi_base_{sid}",
                help    = f"Required: {row['importance_score']:.2f} ({row['level_required']})",
            )

    if use_saved:
        base_skills = {k: saved_skills.get(k, 0.0) for k in [r["skill_id"] for _, r in role_skills.iterrows()]}

    # Baseline score
    baseline = compute_compatibility(base_skills, role_id)
    base_score = baseline["score"]
    base_band, base_color = score_to_band(base_score)

    st.divider()

    # ── Smart recommendations ──────────────────────────────────────────────
    st.markdown("### Step 2 — Smart Recommendations")
    st.caption("These are the skills that would give you the biggest score boost if improved by one level (+0.3).")

    top_recs = recommend_top_improvements(base_skills, role_id, top_n=5)

    if top_recs:
        rec_cols = st.columns(min(len(top_recs), 5))
        for col, rec in zip(rec_cols, top_recs):
            with col:
                st.markdown(
                    f"<div style='border:1px solid #333;border-radius:10px;padding:12px;text-align:center'>"
                    f"<div style='font-size:12px;color:gray'>{rec['category']}</div>"
                    f"<div style='font-weight:500;font-size:13px;margin:4px 0'>{rec['skill_name']}</div>"
                    f"<div style='color:#1D9E75;font-size:18px;font-weight:700'>+{rec['score_gain']:.1f}%</div>"
                    f"<div style='font-size:11px;color:gray'>score gain</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
    else:
        st.info("No gap skills found — you already meet all requirements!")

    st.divider()

    # ── Skill improvement sliders ──────────────────────────────────────────
    st.markdown("### Step 3 — Simulate Your Improvements")
    st.caption("Boost any skills below — drag to see the potential gain.")

    improvements = {}
    for _, row in role_skills.iterrows():
        sid         = row["skill_id"]
        current     = base_skills.get(sid, 0.0)
        max_boost   = round(1.0 - current, 2)

        if max_boost <= 0:
            continue

        boost = st.slider(
            f"📈 {row['skill_name']} (currently `{current:.2f}`, required `{row['importance_score']:.2f}`)",
            min_value = 0.0,
            max_value = max_boost,
            value     = 0.0,
            step      = 0.05,
            key       = f"wi_boost_{sid}",
        )
        if boost > 0:
            improvements[sid] = boost

    st.divider()

    # ── Before / After results ─────────────────────────────────────────────
    st.markdown("### 📊 Before vs After")

    sim = simulate_improvement(base_skills, improvements, role_id)
    after_score = sim["after"]["score"]
    after_band, after_color = score_to_band(after_score)
    delta = sim["score_delta"]

    col_before, col_arrow, col_after = st.columns([2, 1, 2])

    with col_before:
        st.markdown(
            f"<div style='text-align:center;padding:20px;border:2px solid {base_color};"
            f"border-radius:14px;background:{base_color}15'>"
            f"<div style='color:gray;font-size:12px'>BEFORE</div>"
            f"<div style='font-size:44px;font-weight:700;color:{base_color}'>{base_score:.1f}%</div>"
            f"<div style='color:{base_color};font-size:14px'>{base_band}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    with col_arrow:
        arrow_color = "#1D9E75" if delta > 0 else "#888"
        st.markdown(
            f"<div style='text-align:center;padding-top:28px'>"
            f"<div style='font-size:32px'>→</div>"
            f"<div style='color:{arrow_color};font-weight:700;font-size:16px'>"
            f"{'+'if delta>=0 else ''}{delta:.1f}%</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    with col_after:
        st.markdown(
            f"<div style='text-align:center;padding:20px;border:2px solid {after_color};"
            f"border-radius:14px;background:{after_color}15'>"
            f"<div style='color:gray;font-size:12px'>AFTER</div>"
            f"<div style='font-size:44px;font-weight:700;color:{after_color}'>{after_score:.1f}%</div>"
            f"<div style='color:{after_color};font-size:14px'>{after_band}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    if improvements:
        st.markdown("#### Skills you improved:")
        for imp in sim["improved_skills"]:
            skill_name = role_skills[role_skills["skill_id"] == imp["skill_id"]]["skill_name"].values
            name = skill_name[0] if len(skill_name) > 0 else imp["skill_id"]
            st.markdown(
                f"• **{name}**: `{imp['from']:.2f}` → `{imp['to']:.2f}` (+`{imp['delta']:.2f}`)"
            )
    else:
        st.info("Move the sliders above to simulate skill improvements.")

    # ── Side-by-side radar ─────────────────────────────────────────────────
    if improvements:
        st.divider()
        st.markdown("### 🕸️ Radar: Before vs After")
        skill_names, role_vec, base_user_vec = get_skill_vectors(role_id, base_skills)
        _, _, after_user_vec = get_skill_vectors(role_id, sim["updated_skills"])

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown("**Before**")
            render_radar_chart(skill_names, role_vec, base_user_vec,
                               role_title=sel_title, user_label="Before", height=380)
        with col_r2:
            st.markdown("**After**")
            render_radar_chart(skill_names, role_vec, after_user_vec,
                               role_title=sel_title, user_label="After", height=380)