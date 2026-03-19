"""
Career Transition Analyser
───────────────────────────
Computes the skill delta between two roles directly.
Shows transferable skills, skills to gain, skills that become less
important, estimated transition time, radar comparison, and a
suggested learning path for the transition.
"""

import streamlit as st
import plotly.graph_objects as go
from engine.data_loader import load_roles, get_skills_for_role
from config import CATEGORY_COLORS, MIN_IMPORTANCE_THRESHOLD

RESOURCES = {
    "Python":               ["Python.org Official Tutorial", "freeCodeCamp Python", "Automate the Boring Stuff"],
    "SQL":                  ["SQLZoo", "Mode SQL Tutorial", "W3Schools SQL"],
    "Machine Learning":     ["Coursera ML Specialization", "fast.ai", "Kaggle ML Courses"],
    "Deep Learning":        ["fast.ai", "deeplearning.ai", "PyTorch Tutorials"],
    "Data Visualization":   ["Storytelling with Data", "Tableau Public Training", "Kaggle Data Viz"],
    "Statistical Analysis": ["Khan Academy Statistics", "StatQuest YouTube", "Think Stats (free)"],
    "Natural Language Processing": ["HuggingFace NLP Course", "Stanford CS224N", "spaCy Course"],
    "Docker":               ["Docker Official Docs", "Play with Docker", "TechWorld with Nana"],
    "Kubernetes":           ["Kubernetes Tutorials", "KodeKloud free labs", "TechWorld with Nana"],
    "Cloud Platforms (AWS/GCP/Azure)": ["AWS Free Tier", "Google Cloud Skills Boost", "Microsoft Learn"],
    "UX Design":            ["Google UX Design Certificate", "Interaction Design Foundation", "Nielsen Norman"],
    "JavaScript":           ["javascript.info", "freeCodeCamp JS", "Eloquent JavaScript"],
    "Cybersecurity":        ["TryHackMe", "Cybrary", "OWASP Top 10"],
    "Git / Version Control":["Pro Git Book", "GitHub Skills", "Atlassian Git Tutorials"],
    "default":              ["Coursera (audit free)", "freeCodeCamp", "MIT OpenCourseWare"],
}

def get_resources(skill_name):
    return RESOURCES.get(skill_name, RESOURCES["default"])

def estimate_weeks(gap):
    return max(1, min(10, round(gap * 8)))

def compute_transition(from_role_id, to_role_id):
    """
    Compute skill delta between two roles.
    Returns transferable, to_gain, to_deprioritise dicts.
    """
    from_skills = get_skills_for_role(from_role_id)
    to_skills   = get_skills_for_role(to_role_id)

    from_skills = from_skills[from_skills["importance_score"] >= MIN_IMPORTANCE_THRESHOLD]
    to_skills   = to_skills[to_skills["importance_score"] >= MIN_IMPORTANCE_THRESHOLD]

    from_map = dict(zip(from_skills["skill_id"],
                        zip(from_skills["skill_name"],
                            from_skills["importance_score"],
                            from_skills["category"])))
    to_map   = dict(zip(to_skills["skill_id"],
                        zip(to_skills["skill_name"],
                            to_skills["importance_score"],
                            to_skills["category"])))

    transferable     = []  # in both roles
    to_gain          = []  # in target but not in current
    to_deprioritise  = []  # in current but not in target

    all_sids = set(from_map) | set(to_map)

    for sid in all_sids:
        in_from = sid in from_map
        in_to   = sid in to_map

        if in_from and in_to:
            fname, fimp, fcat = from_map[sid]
            tname, timp, tcat = to_map[sid]
            delta = timp - fimp
            transferable.append({
                "skill_id":   sid,
                "skill_name": tname,
                "category":   tcat,
                "from_imp":   round(fimp, 2),
                "to_imp":     round(timp, 2),
                "delta":      round(delta, 2),
            })
        elif in_to and not in_from:
            tname, timp, tcat = to_map[sid]
            to_gain.append({
                "skill_id":   sid,
                "skill_name": tname,
                "category":   tcat,
                "from_imp":   0.0,
                "to_imp":     round(timp, 2),
                "gap":        round(timp, 2),
                "resources":  get_resources(tname),
                "weeks":      estimate_weeks(timp),
            })
        elif in_from and not in_to:
            fname, fimp, fcat = from_map[sid]
            to_deprioritise.append({
                "skill_id":   sid,
                "skill_name": fname,
                "category":   fcat,
                "from_imp":   round(fimp, 2),
                "to_imp":     0.0,
            })

    transferable.sort(key=lambda x: x["to_imp"], reverse=True)
    to_gain.sort(key=lambda x: x["to_imp"], reverse=True)
    to_deprioritise.sort(key=lambda x: x["from_imp"], reverse=True)

    return transferable, to_gain, to_deprioritise


def render_transition_radar(from_title, to_title, from_id, to_id):
    from_skills = get_skills_for_role(from_id)
    to_skills   = get_skills_for_role(to_id)
    from_skills = from_skills[from_skills["importance_score"] >= MIN_IMPORTANCE_THRESHOLD]
    to_skills   = to_skills[to_skills["importance_score"] >= MIN_IMPORTANCE_THRESHOLD]

    from_map = dict(zip(from_skills["skill_name"], from_skills["importance_score"]))
    to_map   = dict(zip(to_skills["skill_name"],   to_skills["importance_score"]))
    all_skills = list(set(from_map) | set(to_map))[:14]

    from_vals = [from_map.get(s, 0.0) for s in all_skills]
    to_vals   = [to_map.get(s, 0.0)   for s in all_skills]

    closed_skills = all_skills + [all_skills[0]]
    from_closed   = from_vals  + [from_vals[0]]
    to_closed     = to_vals    + [to_vals[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=from_closed, theta=closed_skills, fill="toself",
        name=from_title,
        fillcolor="rgba(29,158,117,0.15)",
        line=dict(color="#1D9E75", width=2),
    ))
    fig.add_trace(go.Scatterpolar(
        r=to_closed, theta=closed_skills, fill="toself",
        name=to_title,
        fillcolor="rgba(127,119,221,0.15)",
        line=dict(color="#7F77DD", width=2),
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0,1],
                           gridcolor="rgba(128,128,128,0.2)"),
            bgcolor="rgba(0,0,0,0)",
        ),
        showlegend=True,
        legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
        height=420,
        margin=dict(t=30, b=60, l=60, r=60),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)


def render():
    st.markdown("## Career Transition Analyser")
    st.markdown(
        "Select your **current role** and your **target role** to see exactly "
        "what skills transfer, what you need to gain, and a week-by-week transition plan."
    )
    st.divider()

    roles     = sorted(load_roles(), key=lambda r: r["title"])
    role_map  = {r["title"]: r for r in roles}
    all_titles = [r["title"] for r in roles]
    options   = ["— Select a role —"] + all_titles

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Current Role**")
        from_title = st.selectbox("You are currently a:", options, index=0, key="ct_from")
    with col2:
        st.markdown("**Target Role**")
        to_title = st.selectbox("You want to become a:", options, index=0, key="ct_to")

    if from_title == "— Select a role —" or to_title == "— Select a role —":
        st.info("Select both your current role and target role to begin the transition analysis.")
        return

    if from_title == to_title:
        st.warning("Current and target roles are the same. Please select two different roles.")
        return

    from_role = role_map[from_title]
    to_role   = role_map[to_title]

    analyse_btn = st.button("Analyse My Transition", use_container_width=True, type="primary")

    if not analyse_btn and "ct_result" not in st.session_state:
        return

    if analyse_btn:
        transferable, to_gain, to_deprioritise = compute_transition(
            from_role["role_id"], to_role["role_id"]
        )
        st.session_state["ct_result"] = {
            "transferable":    transferable,
            "to_gain":         to_gain,
            "to_deprioritise": to_deprioritise,
            "from_title":      from_title,
            "to_title":        to_title,
            "from_id":         from_role["role_id"],
            "to_id":           to_role["role_id"],
        }

    r = st.session_state.get("ct_result")
    if not r or r["from_title"] != from_title or r["to_title"] != to_title:
        st.info("Click Analyse My Transition to see results.")
        return

    transferable    = r["transferable"]
    to_gain         = r["to_gain"]
    to_deprioritise = r["to_deprioritise"]
    total_weeks     = sum(s["weeks"] for s in to_gain)

    st.divider()

    # ── Summary cards ──────────────────────────────────────────────────────
    st.markdown(f"### {from_title} → {to_title}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Skills that transfer", len(transferable), help="Skills valuable in both roles")
    c2.metric("Skills to gain",       len(to_gain),      help="New skills needed for target role")
    c3.metric("Skills to deprioritise", len(to_deprioritise), help="Less important in target role")
    c4.metric("Estimated transition", f"{total_weeks} weeks", help="At 8–10 hours per week")

    # Transition difficulty
    difficulty = "Easy" if len(to_gain) <= 3 else "Moderate" if len(to_gain) <= 7 else "Challenging"
    diff_color = "#1D9E75" if difficulty == "Easy" else "#BA7517" if difficulty == "Moderate" else "#E24B4A"
    st.markdown(
        f"<div style='padding:10px 16px;border-left:4px solid {diff_color};"
        f"background:{diff_color}11;border-radius:0 8px 8px 0;margin-bottom:8px'>"
        f"<span style='font-weight:600;color:{diff_color}'>Transition Difficulty: {difficulty}</span>"
        f" — {len(to_gain)} new skills required over approximately {total_weeks} weeks</div>",
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Radar chart ────────────────────────────────────────────────────────
    st.markdown("### Skill Profile Comparison")
    st.caption("Green = your current role profile · Purple = target role profile")
    render_transition_radar(from_title, to_title,
                            from_role["role_id"], to_role["role_id"])

    st.divider()

    # ── Tabs ───────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        f"Skills to Gain ({len(to_gain)})",
        f"Transferable Skills ({len(transferable)})",
        f"Deprioritise ({len(to_deprioritise)})",
        "Transition Learning Path",
    ])

    with tab1:
        st.markdown("#### Skills You Need to Gain")
        st.caption("These skills are required in the target role but not in your current role.")
        if not to_gain:
            st.success("No new skills required — your current role already covers everything!")
        else:
            for s in to_gain:
                color = "#E24B4A" if s["to_imp"] >= 0.8 else "#BA7517" if s["to_imp"] >= 0.6 else "#185FA5"
                st.markdown(
                    f"<div style='display:flex;align-items:center;gap:12px;"
                    f"padding:10px 14px;border:1px solid #333;border-radius:8px;margin-bottom:6px'>"
                    f"<div style='flex:1'>"
                    f"<span style='font-weight:600;font-size:14px'>{s['skill_name']}</span>"
                    f"<span style='color:gray;font-size:12px;margin-left:8px'>{s['category']}</span>"
                    f"</div>"
                    f"<span style='font-size:12px;color:{color};background:{color}22;"
                    f"padding:2px 10px;border-radius:8px'>Importance: {s['to_imp']:.2f}</span>"
                    f"<span style='font-size:12px;color:gray'>{s['weeks']}w</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    with tab2:
        st.markdown("#### Transferable Skills")
        st.caption("These skills are valuable in both roles — your existing knowledge carries over.")
        if not transferable:
            st.info("No directly transferable skills found.")
        else:
            for s in transferable:
                delta_color = "#1D9E75" if s["delta"] >= 0 else "#E24B4A"
                delta_label = f"+{s['delta']:.2f} more important" if s["delta"] > 0 else \
                              f"{s['delta']:.2f} less important" if s["delta"] < 0 else "same importance"
                st.markdown(
                    f"<div style='display:flex;align-items:center;gap:12px;"
                    f"padding:10px 14px;border:1px solid #333;border-radius:8px;margin-bottom:6px'>"
                    f"<div style='flex:1'>"
                    f"<span style='font-weight:600;font-size:14px'>{s['skill_name']}</span>"
                    f"<span style='color:gray;font-size:12px;margin-left:8px'>{s['category']}</span>"
                    f"</div>"
                    f"<span style='font-size:12px;color:gray'>{s['from_imp']:.2f} → {s['to_imp']:.2f}</span>"
                    f"<span style='font-size:11px;color:{delta_color};margin-left:8px'>{delta_label}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    with tab3:
        st.markdown("#### Skills to Deprioritise")
        st.caption("These skills matter in your current role but are less important in the target role.")
        if not to_deprioritise:
            st.info("No skills to deprioritise — all your current skills remain relevant.")
        else:
            for s in to_deprioritise:
                st.markdown(
                    f"<div style='display:flex;align-items:center;gap:12px;"
                    f"padding:10px 14px;border:1px solid #333;border-radius:8px;margin-bottom:6px;"
                    f"opacity:0.7'>"
                    f"<div style='flex:1'>"
                    f"<span style='font-size:14px'>{s['skill_name']}</span>"
                    f"<span style='color:gray;font-size:12px;margin-left:8px'>{s['category']}</span>"
                    f"</div>"
                    f"<span style='font-size:12px;color:gray'>Was: {s['from_imp']:.2f} → Now: less critical</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    with tab4:
        st.markdown("#### Transition Learning Path")
        st.caption(
            f"Prioritised week-by-week plan to transition from **{from_title}** to **{to_title}**. "
            f"Estimated total: **{total_weeks} weeks** at 8–10 hours per week."
        )

        if not to_gain:
            st.success("No learning path needed — you already have all required skills!")
        else:
            # Split into phases by importance
            high   = [s for s in to_gain if s["to_imp"] >= 0.8]
            medium = [s for s in to_gain if 0.6 <= s["to_imp"] < 0.8]
            low    = [s for s in to_gain if s["to_imp"] < 0.6]

            week_counter = 1
            for phase_name, phase_skills, phase_color, phase_desc in [
                ("Phase 1 — Critical Skills",  high,   "#E24B4A", "Highest importance for target role. Start here."),
                ("Phase 2 — Core Skills",      medium, "#BA7517", "Build on Phase 1. Core competencies for the role."),
                ("Phase 3 — Supporting Skills", low,   "#1D9E75", "Final layer. Rounds out your profile."),
            ]:
                if not phase_skills:
                    continue

                st.markdown(
                    f"<div style='border-left:3px solid {phase_color};"
                    f"padding-left:14px;margin-bottom:8px'>"
                    f"<span style='font-weight:600;font-size:15px'>{phase_name}</span><br>"
                    f"<span style='color:gray;font-size:13px'>{phase_desc}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

                for skill in phase_skills:
                    with st.expander(
                        f"Week {week_counter}–{week_counter + skill['weeks'] - 1}  ·  "
                        f"{skill['skill_name']}  ·  "
                        f"Importance: {skill['to_imp']:.2f}",
                        expanded=False,
                    ):
                        col_a, col_b = st.columns([2, 1])
                        with col_a:
                            st.markdown(f"**Category:** {skill['category']}")
                            st.markdown(
                                f"**Why needed:** This skill has an importance score of "
                                f"`{skill['to_imp']:.2f}` in {to_title} but is not required "
                                f"in {from_title}."
                            )
                            st.markdown(f"**Duration:** {skill['weeks']} week{'s' if skill['weeks']>1 else ''}")
                            st.markdown("**Free resources:**")
                            for res in skill["resources"]:
                                st.markdown(f"- {res}")
                        with col_b:
                            st.markdown(
                                f"<div style='text-align:center;padding:16px;"
                                f"border:1px solid {phase_color}33;"
                                f"border-radius:10px;background:{phase_color}11'>"
                                f"<div style='font-size:26px;font-weight:700;color:{phase_color}'>"
                                f"{skill['to_imp']*100:.0f}%</div>"
                                f"<div style='font-size:11px;color:gray'>importance</div>"
                                f"</div>",
                                unsafe_allow_html=True,
                            )
                    week_counter += skill["weeks"]

                st.markdown("")

            st.divider()
            st.markdown(
                f"**Total transition time: {total_weeks} weeks** "
                f"at approximately 8–10 hours per week of focused learning."
            )