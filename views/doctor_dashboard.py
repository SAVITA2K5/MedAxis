"""
views/doctor_dashboard.py
=========================
Doctor-facing dashboard: KPI overview, patient records, patients list,
and editable doctor profile — fully multilingual.
"""

import datetime
import pandas as pd
import streamlit as st

from database import (
    get_doctor_profile, get_hospital_info, get_all_patients,
    get_vitals_log, get_dashboard_stats, update_doctor_profile,
)
from utils.translations import T
from components.profile_cards import render_profile_card
from components import charts


def render(lang: str = "English") -> None:
    """Main entry point for the Doctor Dashboard."""
    uid    = st.session_state.get("user_id", "DOC-889")
    doctor = get_doctor_profile(uid)
    d_name = doctor.get("name", T("doctor", lang) if "doctor" in T.__doc__ or True else "Doctor")

    st.subheader(f"{T('welcome', lang)} {d_name}")

    tab_dash, tab_recs, tab_pats, tab_prof = st.tabs([
        T("tab_dashboard",   lang),
        T("tab_records",     lang),
        T("tab_patients",    lang),
        T("tab_doc_profile", lang),
    ])

    # Pre-load shared data once
    vitals = get_vitals_log()
    df     = pd.DataFrame(vitals)
    stats  = get_dashboard_stats()

    with tab_dash:
        _overview(stats, df, lang)
    with tab_recs:
        _patient_records(df, lang)
    with tab_pats:
        _patients_list(lang)
    with tab_prof:
        _doctor_profile(doctor, lang)


# ─────────────────────────────────────────────────────────────────────────────
def _overview(stats: dict, df: pd.DataFrame, lang: str) -> None:
    """KPI metrics + pain trend + risk donut."""
    k1, k2, k3, k4 = st.columns(4)
    k1.metric(T("total_patients",  lang), stats["total_patients"])
    k2.metric(T("active_alerts",   lang), stats["active_alerts"],
              delta=T("needs_action", lang), delta_color="inverse")
    k3.metric(T("pending_reviews", lang), stats["pending"])
    k4.metric(T("avg_pain",        lang), f"{stats['avg_pain']:.1f}")

    st.divider()

    g1, g2 = st.columns([2, 1])
    with g1:
        charts.pain_trend_chart(df, title=T("pain_trend_title", lang))
    with g2:
        charts.risk_donut_chart(df, title=T("risk_dist_title",  lang))


# ─────────────────────────────────────────────────────────────────────────────
def _patient_records(df: pd.DataFrame, lang: str) -> None:
    """Filterable vitals log table with CSV export."""
    st.markdown(f"### {T('records_heading', lang)}")

    filter_risk = st.multiselect(
        T("filter_risk_label", lang),
        ["High", "Moderate", "Low"],
        default=["High", "Moderate"],
    )

    if df.empty:
        st.info(T("no_records", lang))
        return

    filtered = df if not filter_risk else df[df["risk"].isin(filter_risk)]
    st.dataframe(
        filtered.sort_values("timestamp", ascending=False),
        column_config={
            "timestamp":         T("time_recorded", lang),
            "pain_level":        st.column_config.ProgressColumn(
                                     T("pain_col", lang), min_value=0, max_value=10, format="%d"),
            "risk":              st.column_config.TextColumn(T("risk_col", lang)),
            "ai_recommendation": st.column_config.TextColumn(T("rec_col",  lang), width="large"),
        },
        use_container_width=True,
        hide_index=True,
    )

    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=T("export_csv_btn", lang),
        data=csv,
        file_name=f"medaxis_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
    )


# ─────────────────────────────────────────────────────────────────────────────
def _patients_list(lang: str) -> None:
    """Simple list of all patients under this doctor."""
    st.markdown(f"### {T('patients_heading', lang)}")
    patients = get_all_patients()

    if not patients:
        st.info(T("no_patients", lang))
        return

    rows = []
    for p in patients:
        rows.append({
            T("patient_name_col",      lang): p.get("name", ""),
            T("patient_condition_col", lang): p.get("condition", ""),
            T("patient_contact_col",   lang): p.get("contact", ""),
            "ID":                             p.get("patient_id", ""),
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
def _doctor_profile(doctor: dict, lang: str) -> None:
    """Editable doctor profile card."""
    edit_key = "doctor_edit_mode"
    if edit_key not in st.session_state:
        st.session_state[edit_key] = False

    if not st.session_state[edit_key]:
        # READ mode
        render_profile_card(T("doctor_profile_title", lang), doctor)
        hospital = get_hospital_info(doctor.get("hospital_id", 1))
        render_profile_card(T("hospital_details", lang), hospital)
        st.info(T("doctor_schedule_note", lang))
        if st.button(T("edit_profile_btn", lang), key="doc_edit_btn"):
            st.session_state[edit_key] = True
            st.rerun()
    else:
        # EDIT mode
        st.markdown(f"#### ✏️ {T('doctor_profile_title', lang)}")
        new_specialty = st.text_input(
            T("specialty_label",      lang), value=doctor.get("specialty", ""))
        new_qual      = st.text_input(
            T("qualification_label",  lang), value=doctor.get("qualification", ""))
        new_contact   = st.text_input(
            T("contact_label",        lang), value=doctor.get("contact", ""))
        new_email     = st.text_input(
            T("email_label",          lang), value=doctor.get("email", ""))

        c1, c2 = st.columns(2)
        if c1.button(T("save_profile_btn", lang), type="primary", key="doc_save_btn"):
            ok = update_doctor_profile(
                doctor["doctor_id"],
                {
                    "specialty":     new_specialty,
                    "qualification": new_qual,
                    "contact":       new_contact,
                    "email":         new_email,
                },
            )
            if ok:
                st.success(T("update_success", lang))
                st.session_state[edit_key] = False
                st.rerun()
            else:
                st.error(T("update_error", lang))
        if c2.button(T("cancel", lang), key="doc_cancel_btn"):
            st.session_state[edit_key] = False
            st.rerun()
