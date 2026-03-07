"""
views/login.py
==============
MedAxis Login Page — role selector + per-role credential forms.
"""

import streamlit as st
from auth import validate_patient, validate_doctor, login_patient, login_doctor
from utils.translations import T

_LOGIN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', 'Segoe UI', sans-serif; }

.login-hero {
    text-align: center;
    padding: 28px 0 10px 0;
}
.login-hero h1 {
    font-size: 2.8rem; font-weight: 800;
    color: #0277BD; margin: 8px 0 4px 0;
}
.login-hero p { color: #607D8B; font-size: 1.05rem; margin-bottom: 20px; }

.login-card {
    background: white;
    border-radius: 20px;
    padding: 36px 40px;
    box-shadow: 0 8px 32px rgba(2,119,189,0.13);
    border-top: 5px solid #0277BD;
    margin-bottom: 16px;
}
.login-card-title {
    font-size: 1.5rem; font-weight: 700;
    color: #0277BD; text-align: center; margin-bottom: 4px;
}
.login-card-sub {
    font-size: 0.88rem; color: #90A4AE;
    text-align: center; margin-bottom: 22px;
}
.demo-hint {
    text-align: center; color: #90A4AE;
    font-size: 0.82rem; margin-top: 16px;
    padding: 8px 14px; background: #f5f5f5;
    border-radius: 8px;
}
</style>
"""


def render(lang: str = "English") -> None:
    """Entry point — renders the correct login sub-screen."""
    st.markdown(_LOGIN_CSS, unsafe_allow_html=True)
    screen = st.session_state.get("login_screen", "home")
    if screen == "patient":
        _patient_form(lang)
    elif screen == "doctor":
        _doctor_form(lang)
    else:
        _role_selector(lang)


# ─────────────────────────────────────────────────────────────────────────────
def _role_selector(lang: str) -> None:
    """Landing screen: choose Patient or Doctor."""
    st.markdown(f"""
    <div class="login-hero">
        <img src="https://img.icons8.com/color/96/caduceus.png" width="82"/>
        <h1>{T('app_title', lang)}</h1>
        <p>{T('app_subtitle', lang)}</p>
        <p style="font-size:1.1rem;font-weight:600;color:#37474F;">
            {T('select_role', lang)}
        </p>
    </div>
    """, unsafe_allow_html=True)

    _, c1, c2, _ = st.columns([1, 2, 2, 1])
    with c1:
        if st.button(T("login_as_patient", lang), type="primary",
                     use_container_width=True, key="btn_sel_patient"):
            st.session_state["login_screen"] = "patient"
            st.rerun()
    with c2:
        if st.button(T("login_as_doctor", lang),
                     use_container_width=True, key="btn_sel_doctor"):
            st.session_state["login_screen"] = "doctor"
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
def _patient_form(lang: str) -> None:
    """Patient login form."""
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown(f"""
        <div class="login-card">
            <div class="login-card-title">🧑‍⚕️ {T('patient_login_title', lang)}</div>
            <div class="login-card-sub">{T('app_subtitle', lang)}</div>
        </div>
        """, unsafe_allow_html=True)

        pid = st.text_input(T("patient_id_label", lang),
                            placeholder=T("patient_id_hint", lang), key="p_id")
        pwd = st.text_input(T("password_label", lang),
                            type="password", key="p_pwd")

        c1, c2 = st.columns(2)
        login_clicked = c1.button(T("login_btn", lang), type="primary",
                                  use_container_width=True, key="pat_login_btn")
        if c2.button(T("back_home", lang), use_container_width=True,
                     key="pat_back_btn"):
            st.session_state["login_screen"] = "home"
            st.rerun()

        if login_clicked:
            if validate_patient(pid, pwd):
                login_patient(pid)
                st.session_state["login_screen"] = "home"
                st.rerun()
            else:
                st.error(T("invalid_creds", lang))

        st.markdown(
            f"<div class='demo-hint'>Demo — ID: <b>P-1024</b>"
            f" &nbsp;|&nbsp; {T('password_label', lang)}: <b>patient123</b></div>",
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
def _doctor_form(lang: str) -> None:
    """Doctor login form."""
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown(f"""
        <div class="login-card">
            <div class="login-card-title">👨‍⚕️ {T('doctor_login_title', lang)}</div>
            <div class="login-card-sub">{T('app_subtitle', lang)}</div>
        </div>
        """, unsafe_allow_html=True)

        did = st.text_input(T("doctor_id_label", lang),
                            placeholder=T("doctor_id_hint", lang), key="d_id")
        pwd = st.text_input(T("password_label", lang),
                            type="password", key="d_pwd")

        c1, c2 = st.columns(2)
        login_clicked = c1.button(T("login_btn", lang), type="primary",
                                  use_container_width=True, key="doc_login_btn")
        if c2.button(T("back_home", lang), use_container_width=True,
                     key="doc_back_btn"):
            st.session_state["login_screen"] = "home"
            st.rerun()

        if login_clicked:
            if validate_doctor(did, pwd):
                login_doctor(did)
                st.session_state["login_screen"] = "home"
                st.rerun()
            else:
                st.error(T("invalid_creds", lang))

        st.markdown(
            f"<div class='demo-hint'>Demo — ID: <b>DOC-889</b>"
            f" &nbsp;|&nbsp; {T('password_label', lang)}: <b>doctor123</b></div>",
            unsafe_allow_html=True,
        )
