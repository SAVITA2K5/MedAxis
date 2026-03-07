"""
components/charts.py
====================
Reusable Plotly chart components for MedAxis dashboards.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

# Shared colour map for risk levels
RISK_COLORS = {
    "High":     "#D32F2F",
    "Moderate": "#F57C00",
    "Low":      "#388E3C",
}

_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=42, b=10),
    font=dict(family="Inter, Segoe UI, sans-serif"),
)


def pain_trend_chart(df: pd.DataFrame, title: str = "📈 Pain Trend Analysis") -> None:
    """Area chart of pain level over time, coloured by risk."""
    if df.empty:
        st.info("No vitals data available yet.")
        return
    df_s = df.sort_values("timestamp")
    fig = px.area(
        df_s, x="timestamp", y="pain_level",
        color="risk", markers=True,
        color_discrete_map=RISK_COLORS,
        title=title,
        labels={"pain_level": "Pain Level", "timestamp": ""},
    )
    fig.update_layout(**_LAYOUT, xaxis=dict(showgrid=False),
                      yaxis=dict(gridcolor="#f0f0f0", range=[0, 10]))
    st.plotly_chart(fig, use_container_width=True)


def risk_donut_chart(df: pd.DataFrame, title: str = "⚠️ Risk Distribution") -> None:
    """Donut chart showing proportion of High / Moderate / Low risk readings."""
    if df.empty:
        st.info("No vitals data available yet.")
        return
    fig = px.pie(
        df, names="risk", hole=0.45, color="risk",
        color_discrete_map=RISK_COLORS,
        title=title,
    )
    fig.update_layout(**_LAYOUT, showlegend=True)
    fig.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig, use_container_width=True)


def sleep_trend_chart(df: pd.DataFrame, title: str = "😴 Sleep Hours Trend") -> None:
    """Line chart of sleep hours over time."""
    if df.empty:
        return
    df_s = df.sort_values("timestamp")
    fig = px.line(
        df_s, x="timestamp", y="sleep_hours",
        markers=True, title=title,
        color_discrete_sequence=["#0277BD"],
        labels={"sleep_hours": "Hours", "timestamp": ""},
    )
    fig.add_hline(y=7, line_dash="dot", line_color="#388E3C",
                  annotation_text="Recommended (7 h)")
    fig.update_layout(**_LAYOUT, xaxis=dict(showgrid=False),
                      yaxis=dict(gridcolor="#f0f0f0"))
    st.plotly_chart(fig, use_container_width=True)


def temp_trend_chart(df: pd.DataFrame, title: str = "🌡️ Temperature Trend (°F)") -> None:
    """Line chart of body temperature with fever threshold lines."""
    if df.empty:
        return
    df_s = df.sort_values("timestamp")
    fig = px.line(
        df_s, x="timestamp", y="temp",
        markers=True, title=title,
        color_discrete_sequence=["#E53935"],
        labels={"temp": "°F", "timestamp": ""},
    )
    fig.add_hline(y=98.6,  line_dash="dot", line_color="#388E3C",
                  annotation_text="Normal (98.6°F)")
    fig.add_hline(y=100.4, line_dash="dot", line_color="#D32F2F",
                  annotation_text="Fever (100.4°F)")
    fig.update_layout(**_LAYOUT, xaxis=dict(showgrid=False),
                      yaxis=dict(gridcolor="#f0f0f0"))
    st.plotly_chart(fig, use_container_width=True)
