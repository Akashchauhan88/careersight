"""Overview Page — CareerSight home with clickable module cards."""

import streamlit as st
from config import CATEGORY_COLORS, APP_TITLE, APP_SUBTITLE


def render():
    # Hero section
    st.markdown(
        f"""
        <div style='padding:40px 0 32px 0;border-bottom:1px solid #1e2d3d;margin-bottom:32px'>
            <div style='display:flex;align-items:center;gap:12px;margin-bottom:8px'>
                <span style='font-size:36px'>🔭</span>
                <h1 style='margin:0;font-size:36px;font-weight:700;
                    background:linear-gradient(135deg,#a78bfa,#7F77DD,#1D9E75);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    background-clip:text'>
                    {APP_TITLE}
                </h1>
            </div>
            <p style='color:#8b9ab0;font-size:15px;margin:0 0 20px 0;max-width:600px'>
                {APP_SUBTITLE}
            </p>
            <p style='color:#64748b;font-size:13px;max-width:700px;line-height:1.7;margin:0'>
                CareerSight helps students and early professionals understand where they stand
                in their career journey and what to learn next — combining structured skill gap
                analysis with explainable AI to deliver transparent, evidence-based career guidance.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Coverage stats
    cols = st.columns(4)
    stats = [
        ("63", "Career Roles",    "#7F77DD"),
        ("60", "Tracked Skills",  "#1D9E75"),
        ("545","Role–Skill Pairs","#BA7517"),
        ("9",  "System Modules",  "#185FA5"),
    ]
    for col, (value, label, color) in zip(cols, stats):
        with col:
            st.markdown(
                f"<div style='background:#0f1724;border:1px solid #1e2d3d;"
                f"border-top:3px solid {color};border-radius:12px;padding:20px;text-align:center'>"
                f"<div style='font-size:32px;font-weight:700;color:{color}'>{value}</div>"
                f"<div style='font-size:12px;color:#8b9ab0;margin-top:4px;text-transform:uppercase;"
                f"letter-spacing:0.05em'>{label}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("<div style='margin:32px 0'></div>", unsafe_allow_html=True)

    # System modules — expandable
    st.markdown(
        "<h2 style='font-size:18px;font-weight:600;color:#e2e8f0;margin-bottom:4px'>"
        "System Modules</h2>"
        "<p style='color:#64748b;font-size:12px;margin-bottom:16px'>Click any module to learn more</p>",
        unsafe_allow_html=True,
    )

    modules = [
        ("🗂️", "Career Role Library",        "#7F77DD",
         "Browse 63 career roles across 5 professional domains.",
         "Each role includes a full description, key responsibilities, salary range, demand level, projected growth rate, required tools and technologies, and a three-tier learning roadmap covering Foundation, Intermediate, and Advanced skills."),

        ("📊", "Skill Gap Analysis",          "#1D9E75",
         "Get a weighted compatibility score for your target role.",
         "Rate your current skill levels using sliders. The system calculates a compatibility score using O*NET importance weights, then shows your strengths, skill gaps, and a radar chart comparing your profile against the role requirements."),

        ("🔮", "Skill Improvement Simulator", "#BA7517",
         "Simulate skill improvements before committing to learning.",
         "Boost specific skills hypothetically and see instantly how your compatibility score changes. Side-by-side radar charts show your before and after profile. Smart recommendations highlight which skills give the biggest score improvement."),

        ("🤖", "AI Career Predictor",         "#185FA5",
         "AI-driven top 5 role predictions from your skill profile.",
         "The AI model analyses your full skill profile across all 60 skills and predicts your top 5 best-fit career roles with confidence probabilities. Every prediction is explained using SHAP feature contribution analysis showing which skills drove each decision."),

        ("⚖️", "Role Comparison",             "#7F77DD",
         "Compare up to 4 roles side by side.",
         "Select any combination of roles to compare across salary ranges, projected growth rates, demand levels, skill radar profiles, and learning roadmaps. Auto-loads your AI predicted roles for instant comparison after running the predictor."),

        ("🔄", "Career Transition Analyser",  "#1D9E75",
         "Plan your move from one role to another.",
         "Select your current role and target role to see exactly which skills transfer, which new skills you need to gain, and which become less important. Includes a difficulty rating, estimated transition time, and a week-by-week transition learning plan with free resources."),

        ("🗺️", "Learning Path Generator",     "#BA7517",
         "Week-by-week personalised study plan.",
         "Based on your skill gaps for a target role, the system generates a prioritised learning plan organised into three phases — Critical Skills, Core Skills, and Supporting Skills. Each skill includes estimated study duration and curated free learning resources."),

        ("📄", "Export Report",               "#185FA5",
         "Download your complete career analysis as a PDF.",
         "Generates a structured PDF report with three parts: Part 1 covers your target role analysis, compatibility score, skill profile, and learning path. Part 2 covers AI predicted roles with comparison data. Part 3 covers your career transition analysis if completed."),
    ]

    # Display as 2-column expandable list
    col_a, col_b = st.columns(2)
    for i, (icon, name, color, short, full) in enumerate(modules):
        target_col = col_a if i % 2 == 0 else col_b
        with target_col:
            with st.expander(f"{icon}  {name}", expanded=False):
                st.markdown(
                    f"<div style='padding:4px 0'>"
                    f"<p style='color:#a78bfa;font-size:13px;font-weight:500;margin:0 0 8px'>{short}</p>"
                    f"<p style='color:#8b9ab0;font-size:13px;line-height:1.7;margin:0'>{full}</p>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    st.markdown("<div style='margin:32px 0'></div>", unsafe_allow_html=True)

    # Recommended workflow
    st.markdown(
        "<h2 style='font-size:18px;font-weight:600;color:#e2e8f0;margin-bottom:16px'>"
        "Recommended Workflow</h2>",
        unsafe_allow_html=True,
    )

    steps = [
        ("01", "Browse Roles",       "#7F77DD", "Explore Career Role Library to find roles that interest you"),
        ("02", "Analyse Skills",     "#1D9E75", "Go to Skill Gap Analysis — select a role and rate your skills"),
        ("03", "Simulate & Predict", "#BA7517", "Use Simulator and AI Predictor to explore your options"),
        ("04", "Plan Transition",    "#185FA5", "Use Career Transition Analyser if switching from another role"),
        ("05", "Export Report",      "#7F77DD", "Download your complete PDF career analysis report"),
    ]

    flow_cols = st.columns(5)
    for col, (num, title, color, desc) in zip(flow_cols, steps):
        with col:
            st.markdown(
                f"<div style='background:#0f1724;border:1px solid #1e2d3d;"
                f"border-radius:12px;padding:16px 12px;text-align:center;height:150px'>"
                f"<div style='font-size:26px;font-weight:700;color:{color};opacity:0.5;"
                f"font-family:monospace;margin-bottom:8px'>{num}</div>"
                f"<div style='font-weight:600;font-size:12px;color:#e2e8f0;margin-bottom:6px'>{title}</div>"
                f"<div style='color:#64748b;font-size:11px;line-height:1.5'>{desc}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.divider()

    # Role categories
    st.markdown(
        "<h2 style='font-size:18px;font-weight:600;color:#e2e8f0;margin-bottom:16px'>"
        "Role Categories</h2>",
        unsafe_allow_html=True,
    )

    cats = {
        "Data & AI":            (20, "#7F77DD"),
        "Software Engineering": (13, "#1D9E75"),
        "Product & Analytics":  (13, "#BA7517"),
        "UX & Design":          (9,  "#D85A30"),
        "DevOps & Cloud":       (8,  "#185FA5"),
    }

    for cat, (count, color) in cats.items():
        pct = count / 63
        st.markdown(
            f"<div style='display:flex;align-items:center;gap:14px;margin-bottom:10px'>"
            f"<span style='width:180px;font-size:13px;color:#cbd5e1'>{cat}</span>"
            f"<div style='flex:1;background:#1e2d3d;border-radius:4px;height:8px;overflow:hidden'>"
            f"<div style='width:{pct*100:.0f}%;background:{color};height:100%;border-radius:4px'></div>"
            f"</div>"
            f"<span style='width:28px;text-align:right;font-size:13px;color:#8b9ab0'>{count}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )