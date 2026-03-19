"""Skill Bar Chart Component — horizontal bars comparing user vs role."""

import plotly.graph_objects as go
import streamlit as st


def render_skill_bars(skill_details: list[dict], title: str = "Skill Breakdown") -> None:
    """
    Render a horizontal grouped bar chart: user level vs role importance.

    Parameters
    ----------
    skill_details : list of dicts with keys: skill_name, user_level, importance
    title         : chart title
    """
    if not skill_details:
        st.info("No skill data available.")
        return

    # Sort by importance descending
    sorted_skills = sorted(skill_details, key=lambda x: x["importance"], reverse=True)

    names      = [s["skill_name"] for s in sorted_skills]
    user_vals  = [s["user_level"]  for s in sorted_skills]
    role_vals  = [s["importance"]  for s in sorted_skills]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name            = "Role Requirement",
        y               = names,
        x               = role_vals,
        orientation     = "h",
        marker_color    = "rgba(127, 119, 221, 0.7)",
        hovertemplate   = "<b>%{y}</b><br>Required: %{x:.2f}<extra></extra>",
    ))

    fig.add_trace(go.Bar(
        name            = "Your Level",
        y               = names,
        x               = user_vals,
        orientation     = "h",
        marker_color    = "rgba(29, 158, 117, 0.85)",
        hovertemplate   = "<b>%{y}</b><br>Your level: %{x:.2f}<extra></extra>",
    ))

    fig.update_layout(
        barmode       = "overlay",
        title         = dict(text=title, font=dict(size=15)),
        xaxis         = dict(range=[0, 1.05], title="Skill Level", tickformat=".1f"),
        yaxis         = dict(automargin=True),
        height        = max(300, len(names) * 36 + 100),
        margin        = dict(l=10, r=10, t=50, b=40),
        legend        = dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        paper_bgcolor = "rgba(0,0,0,0)",
        plot_bgcolor  = "rgba(0,0,0,0)",
    )

    fig.update_xaxes(showgrid=True, gridcolor="rgba(128,128,128,0.15)")
    fig.update_yaxes(showgrid=False)

    st.plotly_chart(fig, use_container_width=True)


def render_gap_bars(gaps: list[dict]) -> None:
    """
    Render a bar chart showing only the skill gaps (sorted by gap size).

    Parameters
    ----------
    gaps : list of dicts with keys: skill_name, gap, importance, user_level
    """
    if not gaps:
        st.success("No skill gaps detected — excellent match!")
        return

    sorted_gaps = sorted(gaps, key=lambda x: x["gap"], reverse=True)
    names = [g["skill_name"] for g in sorted_gaps]
    vals  = [g["gap"]        for g in sorted_gaps]

    # Color intensity by gap size
    colors = [
        f"rgba(226, 75, 74, {0.4 + 0.6 * v})" for v in vals
    ]

    fig = go.Figure(go.Bar(
        x             = vals,
        y             = names,
        orientation   = "h",
        marker_color  = colors,
        hovertemplate = "<b>%{y}</b><br>Gap: %{x:.2f}<extra></extra>",
    ))

    fig.update_layout(
        title         = dict(text="Skill Gaps (largest first)", font=dict(size=14)),
        xaxis         = dict(range=[0, 1], title="Gap Size"),
        yaxis         = dict(automargin=True),
        height        = max(250, len(names) * 36 + 80),
        margin        = dict(l=10, r=10, t=50, b=30),
        paper_bgcolor = "rgba(0,0,0,0)",
        plot_bgcolor  = "rgba(0,0,0,0)",
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(128,128,128,0.15)")

    st.plotly_chart(fig, use_container_width=True)
