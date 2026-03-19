"""SHAP Waterfall Plot Component — visualises feature contributions."""

import plotly.graph_objects as go
import streamlit as st


def render_shap_waterfall(shap_features: list[dict], role_title: str) -> None:
    """
    Render a SHAP waterfall chart showing which skills pushed the model
    toward or away from the predicted role.

    Parameters
    ----------
    shap_features : list of dicts with keys: skill_name, shap_value, user_level, direction
    role_title    : name of the predicted role (for the chart title)
    """
    if not shap_features:
        st.info("No SHAP data available.")
        return

    # Sort: most positive first, then most negative
    positives = [f for f in shap_features if f["shap_value"] >= 0]
    negatives = [f for f in shap_features if f["shap_value"] < 0]
    positives.sort(key=lambda x: x["shap_value"], reverse=True)
    negatives.sort(key=lambda x: x["shap_value"])

    ordered = positives + negatives

    names  = [f["skill_name"] for f in ordered]
    values = [f["shap_value"] for f in ordered]
    levels = [f["user_level"] for f in ordered]

    colors = [
        "#1D9E75" if v >= 0 else "#E24B4A"
        for v in values
    ]

    hover_texts = [
        f"<b>{n}</b><br>SHAP value: {v:+.4f}<br>Your skill level: {l:.2f}"
        for n, v, l in zip(names, values, levels)
    ]

    fig = go.Figure(go.Bar(
        x             = values,
        y             = names,
        orientation   = "h",
        marker_color  = colors,
        hovertemplate = "%{customdata}<extra></extra>",
        customdata    = hover_texts,
    ))

    fig.add_vline(x=0, line_width=1, line_color="rgba(128,128,128,0.5)")

    fig.update_layout(
        title = dict(
            text = f"SHAP Feature Contributions → {role_title}",
            font = dict(size=14),
        ),
        xaxis = dict(
            title     = "SHAP Value (contribution to prediction)",
            zeroline  = True,
            zerolinecolor = "rgba(128,128,128,0.4)",
        ),
        yaxis         = dict(automargin=True),
        height        = max(300, len(ordered) * 38 + 100),
        margin        = dict(l=10, r=10, t=60, b=40),
        paper_bgcolor = "rgba(0,0,0,0)",
        plot_bgcolor  = "rgba(0,0,0,0)",
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(128,128,128,0.12)")

    st.plotly_chart(fig, use_container_width=True)

    # Plain-English interpretation
    top_pos = positives[:3] if positives else []
    top_neg = negatives[:3] if negatives else []

    if top_pos:
        pos_names = ", ".join([f"**{f['skill_name']}**" for f in top_pos])
        st.success(f"Skills pushing **toward** {role_title}: {pos_names}")
    if top_neg:
        neg_names = ", ".join([f"**{f['skill_name']}**" for f in top_neg])
        st.error(f"Skills limiting fit for {role_title}: {neg_names}")
