"""Career Role Library — browse and filter all 63 roles."""

import streamlit as st
from engine.data_loader import load_roles
from components.role_card import render_role_card
from config import DEMAND_COLORS


def render():
    st.markdown("## Career Role Library")
    st.markdown("Browse all 63 career roles. Search by name, filter by category or demand level.")
    st.divider()

    roles = sorted(load_roles(), key=lambda r: r["title"])

    col_search, col_cat, col_demand = st.columns([2, 2, 1.5])
    with col_search:
        search = st.text_input("Search roles", placeholder="e.g. Machine Learning, UX, DevOps…")
    with col_cat:
        all_cats = ["All Categories"] + sorted({r["category"] for r in roles})
        sel_cat  = st.selectbox("Category", all_cats)
    with col_demand:
        sel_demand = st.selectbox("Demand", ["All", "High", "Medium", "Low"])

    # Apply filters
    filtered = roles
    if search:
        q = search.lower()
        filtered = [r for r in filtered if
                    q in r["title"].lower() or
                    q in r["description"].lower() or
                    any(q in t.lower() for t in r.get("tools_and_technologies", []))]
    if sel_cat != "All Categories":
        filtered = [r for r in filtered if r["category"] == sel_cat]
    if sel_demand != "All":
        filtered = [r for r in filtered if r["demand_level"] == sel_demand]

    st.caption(f"Showing {len(filtered)} of {len(roles)} roles")

    if not filtered:
        st.warning("No roles match your filters. Try broadening your search.")
        return

    # Show empty prompt if no search/filter applied
    if not search and sel_cat == "All Categories" and sel_demand == "All":
        st.info("Use the search bar or filters above to find roles, or scroll down to browse all.")

    for role in filtered:
        demand_color = DEMAND_COLORS.get(role["demand_level"], "#888")
        with st.expander(
            f"{role['title']}  ·  {role['category']}  ·  "
            f"${role['salary_range']['min']//1000}k–${role['salary_range']['max']//1000}k  ·  "
            f"{role['demand_level']} Demand",
            expanded=False,
        ):
            render_role_card(role, show_roadmap=True)