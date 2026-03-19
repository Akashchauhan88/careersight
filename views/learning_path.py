"""
Learning Path Generator
────────────────────────
Auto-loads role from Skill Gap Analysis or Skill Improvement Simulator.
User can also select a different role manually.
"""

import streamlit as st
from engine.skill_matcher import compute_compatibility
from engine.data_loader import load_roles, get_skills_for_role
from utils.helpers import score_to_band
from config import MIN_IMPORTANCE_THRESHOLD

RESOURCES = {
    "Python":               ["Python.org Official Tutorial", "freeCodeCamp Python Course", "Automate the Boring Stuff (free book)"],
    "SQL":                  ["SQLZoo (interactive)", "Mode SQL Tutorial", "W3Schools SQL"],
    "Machine Learning":     ["Coursera ML Specialization (Andrew Ng)", "fast.ai", "Kaggle ML Courses"],
    "Deep Learning":        ["fast.ai", "deeplearning.ai Specialization", "PyTorch Official Tutorials"],
    "Data Visualization":   ["Storytelling with Data (book)", "Tableau Public Free Training", "Kaggle Data Viz Course"],
    "Statistical Analysis": ["Khan Academy Statistics", "StatQuest YouTube", "Think Stats (free book)"],
    "Natural Language Processing": ["HuggingFace NLP Course (free)", "Stanford CS224N", "spaCy Course (free)"],
    "Computer Vision":      ["fast.ai Computer Vision", "PyTorch CV tutorials", "OpenCV Python tutorials"],
    "Docker":               ["Docker Official Getting Started", "Play with Docker labs", "TechWorld with Nana YouTube"],
    "Kubernetes":           ["Kubernetes Official Tutorials", "KodeKloud free labs", "TechWorld with Nana"],
    "Cloud Platforms (AWS/GCP/Azure)": ["AWS Free Tier + Tutorials", "Google Cloud Skills Boost", "Microsoft Learn (free)"],
    "UX Design":            ["Google UX Design Certificate (Coursera)", "Interaction Design Foundation", "Nielsen Norman Group"],
    "UI Design":            ["Figma Academy (free)", "Refactoring UI (book)", "Laws of UX (free)"],
    "User Research":        ["Nielsen Norman UX Research", "Just Enough Research (book)", "UX Collective"],
    "JavaScript":           ["javascript.info", "freeCodeCamp JS", "Eloquent JavaScript (free)"],
    "React":                ["React Official Docs", "freeCodeCamp React", "Scrimba React"],
    "Cybersecurity":        ["TryHackMe (free tier)", "Cybrary (free)", "OWASP Top 10"],
    "Git / Version Control":["Pro Git Book (free)", "GitHub Skills", "Atlassian Git Tutorials"],
    "Communication":        ["Toastmasters", "Coursera Communication Skills", "HBR Writing Guide"],
    "default":              ["Coursera (audit free)", "freeCodeCamp", "MIT OpenCourseWare", "Kaggle Learn"],
}


def get_resources(skill_name):
    return RESOURCES.get(skill_name, RESOURCES["default"])


def estimate_weeks(gap, importance):
    return max(1, min(12, round(gap * 8 * (0.5 + importance * 0.5))))


def build_plan(gaps):
    """Build phased plan from gaps. Exported for use by export_report."""
    high   = [g for g in gaps if g["importance"] >= 0.8][:4]
    medium = [g for g in gaps if 0.6 <= g["importance"] < 0.8][:4]
    low    = [g for g in gaps if g["importance"] < 0.6][:3]

    phases, week_counter = [], 1
    for phase_name, phase_desc, phase_gaps, phase_color in [
        ("Phase 1 — Foundation Gaps",  "Highest importance skills. Start here.",          high,   "#E24B4A"),
        ("Phase 2 — Core Development", "Build on Phase 1. These round out your profile.", medium, "#BA7517"),
        ("Phase 3 — Skill Polish",     "Final layer. Completes your readiness.",          low,    "#1D9E75"),
    ]:
        if not phase_gaps:
            continue
        items = []
        for gap in phase_gaps:
            weeks = estimate_weeks(gap["gap"], gap["importance"])
            items.append({
                "skill_name":     gap["skill_name"],
                "category":       gap["category"],
                "gap":            gap["gap"],
                "user_level":     gap["user_level"],
                "importance":     gap["importance"],
                "level_required": gap["level_required"],
                "weeks":          weeks,
                "week_start":     week_counter,
                "week_end":       week_counter + weeks - 1,
                "resources":      get_resources(gap["skill_name"]),
            })
            week_counter += weeks
        phases.append({"name": phase_name, "desc": phase_desc,
                       "color": phase_color, "items": items})
    return phases, week_counter - 1


def _init_state():
    for key, val in [
        ("lp_role_id", None), ("lp_role_title", None),
        ("lp_user_skills", {}), ("lp_result", None),
        ("lp_plan", None), ("lp_total_weeks", 0),
        ("lp_generated", False), ("lp_source", None),
    ]:
        if key not in st.session_state:
            st.session_state[key] = val


def render():
    _init_state()

    st.markdown("## Learning Path Generator")
    st.markdown(
        "Get a prioritised week-by-week study plan based on your skill gaps. "
        "Your role auto-loads from Skill Gap Analysis or Skill Improvement Simulator."
    )
    st.divider()

    roles    = sorted(load_roles(), key=lambda r: r["title"])
    role_map = {r["title"]: r for r in roles}
    all_titles = [r["title"] for r in roles]

    # Detect saved sessions
    sa_title   = st.session_state.get("last_role_title", "")
    sa_role_id = st.session_state.get("last_role_id", "")
    sa_skills  = st.session_state.get("last_user_skills", {})

    wi_title   = st.session_state.get("wi_role_title", "")
    wi_role_id = st.session_state.get("wi_role_id", "")
    wi_skills  = st.session_state.get("wi_user_skills", {})

    has_sa = bool(sa_title and sa_role_id and sa_skills)
    has_wi = bool(wi_title and wi_role_id and wi_skills)

    # Source selector
    st.markdown("### Select Role Source")
    source_options = []
    if has_sa:
        source_options.append(f"Skill Gap Analysis — {sa_title}")
    if has_wi and wi_role_id != sa_role_id:
        source_options.append(f"Skill Improvement Simulator — {wi_title}")
    source_options.append("Select a different role manually")

    if source_options:
        source = st.radio("Load role from:", source_options, key="lp_source_radio")
    else:
        source = "Select a different role manually"
        st.caption("Tip: Complete Skill Gap Analysis first to auto-load your role here.")

    manual_mode = "Select a different role" in source

    if not manual_mode:
        if "Skill Gap Analysis" in source:
            active_role_id = sa_role_id
            active_title   = sa_title
            active_skills  = sa_skills
        else:
            active_role_id = wi_role_id
            active_title   = wi_title
            active_skills  = wi_skills

        role = role_map.get(active_title, roles[0])
        st.success(f"Loaded: **{active_title}**")

        # Allow editing skills
        with st.expander("View / edit skill levels", expanded=False):
            role_skills = get_skills_for_role(active_role_id)
            role_skills = role_skills[role_skills["importance_score"] >= MIN_IMPORTANCE_THRESHOLD]
            edited = {}
            for _, row in role_skills.iterrows():
                sid     = row["skill_id"]
                default = float(active_skills.get(sid, 0.0))
                val = st.slider(row["skill_name"], 0.0, 1.0, default, 0.05,
                                key=f"lp_edit_{sid}")
                edited[sid] = val
            active_skills = edited

    else:
        # Manual selection
        col_role, col_cat = st.columns([3, 2])
        with col_cat:
            all_cats = ["All"] + sorted({r["category"] for r in roles})
            sel_cat  = st.selectbox("Filter by category", all_cats, key="lp_cat")
        with col_role:
            filtered  = roles if sel_cat == "All" else [r for r in roles if r["category"] == sel_cat]
            f_titles  = [r["title"] for r in filtered]
            options   = ["— Select a role —"] + f_titles
            prev      = st.session_state["lp_role_title"]
            def_idx   = options.index(prev) if prev in options else 0
            sel_title = st.selectbox("Select target role", options, index=def_idx, key="lp_role_sel")

        if sel_title == "— Select a role —":
            st.info("Select a target role above to generate your learning path.")
            return

        role           = role_map[sel_title]
        active_role_id = role["role_id"]
        active_title   = sel_title

        role_skills = get_skills_for_role(active_role_id)
        role_skills = role_skills[role_skills["importance_score"] >= MIN_IMPORTANCE_THRESHOLD]

        # Reset if role changed
        if st.session_state["lp_role_id"] != active_role_id:
            st.session_state["lp_user_skills"] = {}
            st.session_state["lp_result"]      = None
            st.session_state["lp_plan"]        = None
            st.session_state["lp_generated"]   = False

        st.markdown("### Rate your current skill levels")
        st.caption("0.0 = No knowledge · 0.5 = Working knowledge · 1.0 = Expert")
        active_skills = {}
        for cat in role_skills["category"].unique():
            cat_skills = role_skills[role_skills["category"] == cat]
            st.markdown(f"**{cat}**")
            for _, row in cat_skills.iterrows():
                sid     = row["skill_id"]
                default = float(st.session_state["lp_user_skills"].get(sid, 0.0))
                val = st.slider(
                    f"{row['skill_name']} (required: {row['importance_score']:.1f})",
                    0.0, 1.0, default, 0.05, key=f"lp_s_{active_role_id}_{sid}",
                )
                active_skills[sid] = val

    # Save to session
    st.session_state["lp_role_id"]     = active_role_id
    st.session_state["lp_role_title"]  = active_title
    st.session_state["lp_user_skills"] = active_skills

    st.divider()
    gen_btn = st.button("Generate My Learning Path", use_container_width=True, type="primary")

    if gen_btn:
        result = compute_compatibility(active_skills, active_role_id)
        phases, total_weeks = build_plan(result["gaps"])
        st.session_state["lp_result"]      = result
        st.session_state["lp_plan"]        = phases
        st.session_state["lp_total_weeks"] = total_weeks
        st.session_state["lp_generated"]   = True

    if not st.session_state["lp_generated"]:
        st.info("Click Generate to get your personalised study plan.")
        return

    result      = st.session_state["lp_result"]
    phases      = st.session_state["lp_plan"]
    total_weeks = st.session_state["lp_total_weeks"]
    score       = result["score"]
    band, color = score_to_band(score)

    if not result["gaps"]:
        st.success(f"Your compatibility with {active_title} is {score:.1f}% — no significant gaps found!")
        return

    st.divider()
    st.markdown(f"### Learning Path — {active_title}")
    col_s, col_i = st.columns([1, 3])
    with col_s:
        st.markdown(
            f"<div style='text-align:center;padding:20px;border:2px solid {color};"
            f"border-radius:14px;background:{color}15'>"
            f"<div style='font-size:40px;font-weight:700;color:{color}'>{score:.1f}%</div>"
            f"<div style='color:{color};font-size:13px'>{band}</div>"
            f"<div style='color:gray;font-size:11px;margin-top:4px'>Current readiness</div>"
            f"</div>", unsafe_allow_html=True,
        )
    with col_i:
        st.markdown(f"""
**Target Role:** {active_title}
**Skills to improve:** {len(result['gaps'])}
**Estimated total study time:** {total_weeks} weeks
""")

    st.divider()
    st.markdown("### Study Plan")
    for phase in phases:
        st.markdown(
            f"<div style='border-left:3px solid {phase['color']};padding-left:14px;margin-bottom:8px'>"
            f"<span style='font-weight:600;font-size:15px'>{phase['name']}</span><br>"
            f"<span style='color:gray;font-size:13px'>{phase['desc']}</span>"
            f"</div>", unsafe_allow_html=True,
        )
        for item in phase["items"]:
            with st.expander(
                f"Week {item['week_start']}–{item['week_end']}  ·  "
                f"{item['skill_name']}  ·  Gap: {item['gap']:.2f}  ·  {item['level_required']}",
                expanded=False,
            ):
                col_a, col_b = st.columns([2, 1])
                with col_a:
                    st.markdown(f"**Category:** {item['category']}")
                    st.markdown(f"**Current:** `{item['user_level']:.2f}` → **Target:** `{item['importance']:.2f}`")
                    st.markdown(f"**Duration:** {item['weeks']} week{'s' if item['weeks']>1 else ''}")
                    st.markdown("**Resources:**")
                    for res in item["resources"]:
                        st.markdown(f"- {res}")
                with col_b:
                    st.markdown(
                        f"<div style='text-align:center;padding:16px;border:1px solid {phase['color']}33;"
                        f"border-radius:10px;background:{phase['color']}11'>"
                        f"<div style='font-size:28px;font-weight:700;color:{phase['color']}'>"
                        f"{item['gap']*100:.0f}%</div>"
                        f"<div style='font-size:11px;color:gray'>gap to close</div>"
                        f"</div>", unsafe_allow_html=True,
                    )
        st.markdown("")

    st.divider()
    st.markdown(f"**Total: {total_weeks} weeks** at approximately 8–10 hours per week.")
    st.caption("Go to Export Report to download this plan as a PDF.")