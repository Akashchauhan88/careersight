"""Role Comparison Page — step by step debug."""

import streamlit as st

def render():
    st.markdown("## Role Comparison")
    st.divider()

    from engine.data_loader import load_roles, get_skills_for_role
    from utils.helpers import format_salary, format_growth
    from config import CATEGORY_COLORS, DEMAND_COLORS
    import plotly.graph_objects as go

    roles      = sorted(load_roles(), key=lambda r: r["title"])
    title_map  = {r["title"]: r for r in roles}
    all_titles = [r["title"] for r in roles]

    predicted_titles = []
    raw = st.session_state.get("ai_predictions", None)
    if raw and isinstance(raw, list):
        for p in raw:
            if isinstance(p, dict) and "title" in p:
                t = str(p["title"])
                if t in title_map:
                    predicted_titles.append(t)
        predicted_titles = list(dict.fromkeys(predicted_titles))[:4]

    if predicted_titles:
        use_ai = st.radio("Load from:", ["AI Career Predictor results", "Select manually"], key="comp_src") == "AI Career Predictor results"
    else:
        use_ai = False

    if use_ai:
        selected_titles = st.multiselect("Edit selection", options=all_titles, default=predicted_titles, max_selections=4, key="comp_ai_sel")
    else:
        selected_titles = st.multiselect("Choose 2–4 roles", options=all_titles, default=[], max_selections=4, key="comp_man_sel")

    if not selected_titles or len(selected_titles) < 2:
        st.info("Select at least 2 roles.")
        return

    selected_roles = [title_map[t] for t in selected_titles if t in title_map]

    # Overview cards
    st.divider()
    st.markdown("### Overview")
    cols = st.columns(len(selected_roles))
    for col, role in zip(cols, selected_roles):
        dc = DEMAND_COLORS.get(role.get("demand_level","Medium"), "#888")
        cc = CATEGORY_COLORS.get(role.get("category",""), "#888")
        with col:
            st.markdown(
                f"<div style='border:1px solid #333;border-radius:12px;padding:14px'>"
                f"<div style='font-weight:600;font-size:13px;margin-bottom:5px'>{role['title']}</div>"
                f"<div style='font-size:11px;color:{cc};margin-bottom:6px'>{role.get('category','')}</div>"
                f"<div style='font-size:12px;margin-bottom:3px'>💰 {format_salary(role['salary_range'])}</div>"
                f"<div style='font-size:12px;margin-bottom:3px'>📈 {format_growth(role.get('growth_rate',0))}</div>"
                f"<span style='font-size:11px;background:{dc}22;color:{dc};"
                f"padding:2px 8px;border-radius:8px'>{role.get('demand_level','–')} Demand</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.divider()
    tab1, tab2, tab3, tab4 = st.tabs(["Salary", "Growth", "Skill Radar", "Roadmaps"])

    with tab1:
        titles = [r["title"] for r in selected_roles]
        mins   = [r["salary_range"]["min"] for r in selected_roles]
        maxs   = [r["salary_range"]["max"] for r in selected_roles]
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Min", x=titles, y=mins, marker_color="rgba(29,158,117,0.85)"))
        fig.add_trace(go.Bar(name="Max", x=titles, y=maxs, marker_color="rgba(127,119,221,0.85)"))
        fig.update_layout(barmode="overlay", height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        titles = [r["title"] for r in selected_roles]
        rates  = [r.get("growth_rate", 0) for r in selected_roles]
        clrs   = [CATEGORY_COLORS.get(r["category"], "#888") for r in selected_roles]
        fig2 = go.Figure(go.Bar(x=titles, y=rates, marker_color=clrs))
        fig2.update_layout(height=280, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        from collections import Counter
        from components.radar_chart import render_comparison_radar
        skill_counter   = Counter()
        role_skill_maps = {}
        for role in selected_roles:
            rs = get_skills_for_role(role["role_id"])
            rs = rs[rs["importance_score"] >= 0.5]
            role_skill_maps[role["title"]] = dict(zip(rs["skill_name"], rs["importance_score"]))
            for s in rs["skill_name"]:
                skill_counter[s] += 1
        shared = [s for s, c in skill_counter.most_common(12) if c >= 1]
        if shared:
            color_list = list(CATEGORY_COLORS.values())
            vectors = []
            for i, role in enumerate(selected_roles):
                vals = [role_skill_maps[role["title"]].get(s, 0.0) for s in shared]
                vectors.append((role["title"], vals, color_list[i % len(color_list)]))
            render_comparison_radar(shared, vectors)

    with tab4:
        for role in selected_roles:
            roadmap = role.get("learning_roadmap", {})
            with st.expander(role["title"], expanded=False):
                c1, c2, c3 = st.columns(3)
                for col, (name, key, color) in zip([c1,c2,c3],[
                    ("Foundation","foundation","#1D9E75"),
                    ("Intermediate","intermediate","#BA7517"),
                    ("Advanced","advanced","#7F77DD"),
                ]):
                    with col:
                        st.markdown(f"**{name}**")
                        for item in roadmap.get(key, []):
                            st.markdown(f"• {item}")

    st.divider()
    st.markdown("### Key Insights")
    best_sal = max(selected_roles, key=lambda r: r["salary_range"]["max"])
    best_gr  = max(selected_roles, key=lambda r: r.get("growth_rate", 0))
    st.markdown(f"- **Highest earning:** {best_sal['title']}")
    st.markdown(f"- **Fastest growing:** {best_gr['title']}")