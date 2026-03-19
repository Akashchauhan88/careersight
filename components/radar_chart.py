"""Reusable Plotly radar chart components."""

import plotly.graph_objects as go
import streamlit as st

# Fixed rgba colors for the comparison radar - no dynamic conversion
TRACE_COLORS = [
    {"line": "#7F77DD", "fill": "rgba(127, 119, 221, 0.12)"},
    {"line": "#1D9E75", "fill": "rgba(29, 158, 117, 0.12)"},
    {"line": "#D85A30", "fill": "rgba(216, 90, 48, 0.12)"},
    {"line": "#185FA5", "fill": "rgba(24, 95, 165, 0.12)"},
    {"line": "#BA7517", "fill": "rgba(186, 117, 23, 0.12)"},
]


def render_radar_chart(
    skill_names: list,
    role_vector: list,
    user_vector: list,
    role_title: str = "Role Requirement",
    user_label: str = "Your Skills",
    height: int = 450,
) -> None:
    names_closed = skill_names + [skill_names[0]]
    role_closed  = role_vector  + [role_vector[0]]
    user_closed  = user_vector  + [user_vector[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r             = role_closed,
        theta         = names_closed,
        fill          = "toself",
        name          = role_title,
        fillcolor     = "rgba(127, 119, 221, 0.18)",
        line          = dict(color="#7F77DD", width=2),
        hovertemplate = "<b>%{theta}</b><br>Required: %{r:.2f}<extra></extra>",
    ))

    fig.add_trace(go.Scatterpolar(
        r             = user_closed,
        theta         = names_closed,
        fill          = "toself",
        name          = user_label,
        fillcolor     = "rgba(29, 158, 117, 0.22)",
        line          = dict(color="#1D9E75", width=2.5),
        hovertemplate = "<b>%{theta}</b><br>Your level: %{r:.2f}<extra></extra>",
    ))

    fig.update_layout(
        polar = dict(
            radialaxis  = dict(visible=True, range=[0, 1],
                               gridcolor="rgba(128,128,128,0.2)"),
            angularaxis = dict(tickfont=dict(size=11)),
            bgcolor     = "rgba(0,0,0,0)",
        ),
        showlegend    = True,
        legend        = dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        height        = height,
        margin        = dict(t=30, b=60, l=60, r=60),
        paper_bgcolor = "rgba(0,0,0,0)",
        plot_bgcolor  = "rgba(0,0,0,0)",
    )

    st.plotly_chart(fig, use_container_width=True)


def render_comparison_radar(
    skill_names: list,
    vectors: list,
    height: int = 500,
) -> None:
    names_closed = skill_names + [skill_names[0]]

    fig = go.Figure()

    for i, (label, values, _) in enumerate(vectors):
        c           = TRACE_COLORS[i % len(TRACE_COLORS)]
        vals_closed = values + [values[0]]
        fig.add_trace(go.Scatterpolar(
            r         = vals_closed,
            theta     = names_closed,
            fill      = "toself",
            name      = label,
            fillcolor = c["fill"],
            line      = dict(color=c["line"], width=2),
        ))

    fig.update_layout(
        polar = dict(
            radialaxis = dict(visible=True, range=[0, 1],
                              gridcolor="rgba(128,128,128,0.2)"),
            bgcolor    = "rgba(0,0,0,0)",
        ),
        showlegend    = True,
        legend        = dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        height        = height,
        margin        = dict(t=30, b=80, l=60, r=60),
        paper_bgcolor = "rgba(0,0,0,0)",
        plot_bgcolor  = "rgba(0,0,0,0)",
    )

    st.plotly_chart(fig, use_container_width=True)