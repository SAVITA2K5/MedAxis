"""
views/patient_dashboard.py
===========================
Patient-facing dashboard: Health Check-In, Profile, Hospital Info, Health History.
"""

import datetime
import pandas as pd
import streamlit as st

from database import (
    get_patient_profile, get_doctor_profile, get_hospital_info,
    get_vitals_log, save_vitals, update_patient_profile,
)
from utils.translations import T
from utils.ai_engine import assess_risk
from components.profile_cards import render_profile_card
from components import charts


def render(lang: str = "English") -> None:
    """Main entry point for the Patient Dashboard."""
    uid     = st.session_state.get("user_id", "P-1024")
    patient = get_patient_profile(uid)
    p_name  = patient.get("name", T("patient", lang))

    st.subheader(f"{T('welcome', lang)} {p_name}")

    tab1, tab2, tab3, tab4 = st.tabs([
        T("tab_checkin",  lang),
        T("tab_profile",  lang),
        T("tab_hospital", lang),
        T("tab_history",  lang),
    ])

    with tab1:
        _health_checkin(patient, lang)
    with tab2:
        _patient_profile(patient, lang)
    with tab3:
        _hospital_info(patient, lang)
    with tab4:
        _health_history(uid, lang)


# ─────────────────────────────────────────────────────────────────────────────
def _health_checkin(patient: dict, lang: str) -> None:
    """Daily vitals input form + AI risk result."""
    st.markdown(f"### {T('daily_vitals_heading', lang)}")

    activity_opts = [
        T("activity_low",    lang),
        T("activity_medium", lang),
        T("activity_high",   lang),
    ]

    with st.form("vitals_form"):
        c1, c2 = st.columns(2)
        with c1:
            pain     = st.slider(T("pain_label",     lang), 0, 10, 2)
            activity = st.selectbox(T("activity_label", lang), activity_opts)
        with c2:
            sleep = st.number_input(T("sleep_label", lang), 0.0, 24.0, 7.0, 0.5)
            temp  = st.number_input(T("temp_label",  lang), 90.0, 110.0, 98.6, 0.1)

        submitted = st.form_submit_button(T("submit_vitals", lang),
                                          use_container_width=True)

    if submitted:
        risk, msg, alert = assess_risk(pain, sleep, activity, temp, lang)

        st.divider()
        st.markdown(f"### {T('risk_score', lang)}")
        r_col, m_col = st.columns([1, 3])
        with r_col:
            risk_display = T(f"risk_{risk.lower()}", lang)
            if risk == "High":
                st.error(f"## {risk_display}")
            elif risk == "Moderate":
                st.warning(f"## {risk_display}")
            else:
                st.success(f"## {risk_display}")
        with m_col:
            st.info(f"**{T('ai_recommendation', lang)}:** {msg}")

        pid   = patient.get("patient_id", "P-1024")
        pname = patient.get("name", "Patient")
        if save_vitals(pid, pname, pain, sleep, activity, temp, risk, alert, msg):
            st.success(T("vitals_saved", lang))
        else:
            st.error(T("vitals_error", lang))


# ─────────────────────────────────────────────────────────────────────────────
def _patient_profile(patient: dict, lang: str) -> None:
    """Editable patient biodata card."""
    st.markdown(f"### {T('biodata_heading', lang)}")

    edit_key = "patient_edit_mode"
    if edit_key not in st.session_state:
        st.session_state[edit_key] = False

    if not st.session_state[edit_key]:
        # READ mode
        render_profile_card(T("patient_profile_title", lang), patient)
        st.warning(T("profile_update_note", lang))
        if st.button(T("edit_biodata_btn", lang), key="pat_edit_btn"):
            st.session_state[edit_key] = True
            st.rerun()
    else:
        # EDIT mode
        st.markdown("#### ✏️ " + T("biodata_heading", lang))
        new_name      = st.text_input(T("name_label",      lang), value=patient.get("name", ""))
        new_age       = st.number_input(T("age_label",     lang), 0, 120, int(patient.get("age") or 0))
        new_condition = st.text_input(T("condition_label", lang), value=patient.get("condition", ""))

        c1, c2 = st.columns(2)
        if c1.button(T("save_biodata_btn", lang), type="primary", key="pat_save_btn"):
            ok = update_patient_profile(
                patient["patient_id"],
                {"name": new_name, "age": int(new_age), "condition": new_condition},
            )
            if ok:
                st.success(T("update_success", lang))
                st.session_state[edit_key] = False
                st.rerun()
            else:
                st.error(T("update_error", lang))
        if c2.button(T("cancel", lang), key="pat_cancel_btn"):
            st.session_state[edit_key] = False
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
def _hospital_info(patient: dict, lang: str) -> None:
    """Doctor and hospital info cards."""
    doctor        = get_doctor_profile(patient.get("doctor_id", "DOC-889"))
    hospital_info = get_hospital_info(hospital_id=1)

    col_doc, col_hosp = st.columns(2)
    with col_doc:
        render_profile_card(T("assigned_specialist", lang), doctor)
    with col_hosp:
        render_profile_card(T("hospital_details", lang), hospital_info)


# ─────────────────────────────────────────────────────────────────────────────
def _health_history(patient_id: str, lang: str) -> None:
    """Historical vitals charts for the patient."""
    vitals = get_vitals_log(patient_id=patient_id)
    df     = pd.DataFrame(vitals)

    if df.empty:
        st.info(T("no_records", lang))
        return

    c1, c2 = st.columns(2)
    with c1:
        charts.pain_trend_chart(df,  title=T("pain_trend_title",  lang))
        charts.temp_trend_chart(df,  title=T("temp_trend_title",  lang))
    with c2:
        charts.risk_donut_chart(df,  title=T("risk_dist_title",   lang))
        charts.sleep_trend_chart(df, title=T("sleep_trend_title", lang))
