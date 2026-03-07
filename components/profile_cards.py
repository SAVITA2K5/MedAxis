"""
components/profile_cards.py
============================
Reusable HTML/CSS profile card components for MedAxis.
"""

import streamlit as st

_SKIP_KEYS = {"hospital_id", "doctor_id", "patient_id", "log_id"}

_CARD_CSS = """
<style>
.med-card {
    background: #ffffff;
    padding: 22px 26px;
    border-radius: 14px;
    border-left: 5px solid #0277BD;
    box-shadow: 0 4px 18px rgba(2, 119, 189, 0.10);
    margin-bottom: 18px;
}
.med-card h4 {
    color: #0277BD;
    margin: 0 0 10px 0;
    font-size: 1.05rem;
    font-weight: 700;
}
.med-card hr { border: 1px solid #E3F2FD; margin: 8px 0 12px 0; }
.med-card .row { margin: 6px 0; font-size: 0.92rem; }
.med-card .lbl { color: #0277BD; font-weight: 600; margin-right: 4px; }
.med-card .val { color: #333; }

/* Risk badges */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
}
.badge-high     { background:#FFEBEE; color:#C62828; }
.badge-moderate { background:#FFF3E0; color:#E65100; }
.badge-low      { background:#E8F5E9; color:#2E7D32; }
.badge-normal   { background:#E3F2FD; color:#0277BD; }

/* KPI metric card */
.kpi-card {
    background: white;
    border-radius: 12px;
    padding: 18px 20px;
    text-align: center;
    box-shadow: 0 2px 10px rgba(0,0,0,0.07);
    border-top: 4px solid #0277BD;
}
.kpi-value { font-size: 2.2rem; font-weight: 800; color: #0277BD; }
.kpi-label { font-size: 0.82rem; color: #607D8B; margin-top: 4px; }
</style>
"""

_css_injected = False


def inject_css() -> None:
    """Inject shared card CSS once per page render."""
    global _css_injected
    if not _css_injected:
        st.markdown(_CARD_CSS, unsafe_allow_html=True)
        _css_injected = True


def render_profile_card(title: str, data: dict) -> None:
    """Render a labelled profile card from a dict, skipping internal DB keys."""
    inject_css()
    rows_html = ""
    for key, value in data.items():
        if key in _SKIP_KEYS or value is None:
            continue
        label = key.replace("_", " ").title()
        rows_html += (
            f"<div class='row'>"
            f"<span class='lbl'>{label}:</span>"
            f"<span class='val'>{value}</span>"
            f"</div>"
        )
    st.markdown(
        f"<div class='med-card'><h4>{title}</h4><hr/>{rows_html}</div>",
        unsafe_allow_html=True,
    )


def risk_badge_html(risk_level: str) -> str:
    """Return an inline HTML risk badge string."""
    css = {
        "High":     "badge-high",
        "Moderate": "badge-moderate",
        "Low":      "badge-low",
    }.get(risk_level, "badge-normal")
    return f"<span class='badge {css}'>{risk_level}</span>"


def render_kpi(label: str, value, delta: str | None = None,
               delta_color: str = "normal") -> None:
    """Render a styled KPI card using st.metric."""
    inject_css()
    st.metric(label=label, value=value, delta=delta, delta_color=delta_color)
