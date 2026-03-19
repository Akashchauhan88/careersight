"""Role Card Component — renders a rich info card for a single role."""

import streamlit as st
from utils.helpers import format_salary, format_growth
from config import DEMAND_COLORS, CATEGORY_COLORS


def render_role_card(role: dict, show_roadmap: bool = True) -> None:
    demand_color   = DEMAND_COLORS.get(role.get("demand_level", "Medium"), "#888")
    category_color = CATEGORY_COLORS.get(role.get("category", ""), "#888")

    col_title, col_badges = st.columns([3, 2])
    with col_title:
        st.markdown(f"### {role['title']}")
        st.markdown(
            f"<span style='color:{category_color};font-weight:500;font-size:13px'>"
            f"● {role['category']} · {role.get('subcategory','')}</span>",
            unsafe_allow_html=True,
        )
    with col_badges:
        demand = role.get("demand_level", "–")
        st.markdown(
            f"<div style='text-align:right;margin-top:8px'>"
            f"<span style='background:{demand_color}22;color:{demand_color};"
            f"padding:4px 10px;border-radius:12px;font-size:12px;font-weight:500'>"
            f"{demand} Demand</span></div>",
            unsafe_allow_html=True,
        )

    st.markdown(f"_{role['description']}_")
    st.divider()

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("💰 Salary Range", format_salary(role["salary_range"]))
    with c2:
        st.metric("📈 Growth Rate", format_growth(role.get("growth_rate", 0)))
    with c3:
        st.metric("🏷️ Category", role["category"])

    st.divider()

    st.markdown("**📋 Key Responsibilities**")
    for resp in role.get("responsibilities", []):
        st.markdown(f"- {resp}")

    st.divider()

    focus = role.get("focus_areas", [])
    if focus:
        st.markdown("**Focus Areas:** " + " · ".join([f"`{f}`" for f in focus]))

    tools = role.get("tools_and_technologies", [])
    if tools:
        st.markdown("**Tools & Technologies:** " + " · ".join([f"`{t}`" for t in tools]))

    if show_roadmap:
        roadmap = role.get("learning_roadmap", {})
        if roadmap:
            st.markdown("#### 🗺️ Learning Roadmap")
            cols = st.columns(3)
            tiers = [
                ("🌱 Foundation",   roadmap.get("foundation", []),   "#1D9E75"),
                ("⚡ Intermediate", roadmap.get("intermediate", []), "#BA7517"),
                ("🚀 Advanced",     roadmap.get("advanced", []),     "#7F77DD"),
            ]
            for col, (tier_name, items, color) in zip(cols, tiers):
                with col:
                    st.markdown(
                        f"<p style='color:{color};font-weight:500;margin-bottom:6px'>"
                        f"{tier_name}</p>",
                        unsafe_allow_html=True,
                    )
                    for item in items:
                        st.markdown(f"• {item}")

    reason = role.get("demand_reason", "")
    if reason:
        st.info(f"**Why this role is in demand:** {reason}")