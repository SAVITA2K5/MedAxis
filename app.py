"""
app.py — MedAxis Entry Point & Router
======================================
Application flow:
  Splash Screen  →  Login Page  →  Patient Dashboard
                                →  Doctor  Dashboard

Session state keys used:
  splash_done  : bool  — has the splash been shown?
  logged_in    : bool  — is a user authenticated?
  role         : str   — "patient" | "doctor"
  user_id      : str   — patient_id or doctor_id
  login_screen : str   — "home" | "patient" | "doctor"
  lang         : str   — "English" | "Hindi" | "Tamil"
"""

import datetime
import streamlit as st

# ── Local modules ─────────────────────────────────────────────────────────────
from database import init_db
from auth import is_logged_in, current_role, logout
from utils.translations import T
import components.splash_screen as splash_screen
import views.login as login_view
import views.patient_dashboard as patient_view
import views.doctor_dashboard as doctor_view

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  (must be the very first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MedAxis — Smart Healthcare Intelligence",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# DATABASE INIT  (once per session)
# ─────────────────────────────────────────────────────────────────────────────
if "db_initialized" not in st.session_state:
    with st.spinner("🔌 Connecting to database..."):
        ok = init_db()
    st.session_state["db_initialized"] = ok
    if not ok:
        st.error("⚠️ Could not connect to PostgreSQL. "
                 "Check your `.streamlit/secrets.toml` credentials.")
        st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE DEFAULTS
# ─────────────────────────────────────────────────────────────────────────────
st.session_state.setdefault("splash_done",   False)
st.session_state.setdefault("logged_in",     False)
st.session_state.setdefault("role",          None)
st.session_state.setdefault("user_id",       None)
st.session_state.setdefault("login_screen",  "home")
st.session_state.setdefault("lang",          "English")

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}
.stApp {
    background: linear-gradient(135deg, #f0f8ff 0%, #e8f4fd 100%);
}
h1, h2, h3, h4 { color: #0277BD; }

/* ── Hide Streamlit chrome (toolbar, deploy button, main menu) ── */
[data-testid="stToolbar"]          { display: none !important; }
[data-testid="stDecoration"]       { display: none !important; }
[data-testid="stStatusWidget"]     { display: none !important; }
#MainMenu                          { display: none !important; }
footer                             { display: none !important; }
header [data-testid="stHeader"]    { display: none !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffffff 0%, #f7fbff 100%);
    border-right: 1px solid #e0e0e0;
}

/* Metrics */
[data-testid="stMetricValue"] {
    font-size: 2rem !important;
    color: #0277BD;
    font-weight: 800;
}

/* Tab labels */
.stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
    font-size: 1.0rem;
    font-weight: 600;
}

/* Dividers */
hr { border-color: #E3F2FD !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SPLASH SCREEN  (show once at the very start)
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state["splash_done"]:
    # Language might not be picked yet — use English for splash
    splash_screen.show(
        tagline=T("splash_tagline", "English"),
        loading_text=T("splash_loading", "English"),
        duration=2.8,
    )
    st.stop()   # splash_screen.show() calls st.rerun() internally; this is a safety guard


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR  (always visible after splash)
# ─────────────────────────────────────────────────────────────────────────────
def _render_sidebar() -> str:
    """Render sidebar, return selected language."""
    st.sidebar.image("https://img.icons8.com/color/96/caduceus.png", width=60)
    st.sidebar.markdown(
        "<h2 style='margin:4px 0 18px 0; color:#0277BD; font-weight:800;'>MedAxis</h2>",
        unsafe_allow_html=True,
    )

    lang = st.sidebar.radio(
        T("lang_selector", "English"),
        ["English", "Hindi", "Tamil"],
        key="lang_radio",
    )
    st.session_state["lang"] = lang

    # Logout (only when logged in)
    if is_logged_in():
        st.sidebar.markdown("---")
        if st.sidebar.button(T("logout", lang), use_container_width=True,
                             key="sidebar_logout"):
            logout()
            st.rerun()

    return lang


# ─────────────────────────────────────────────────────────────────────────────
# PAGE HEADER
# ─────────────────────────────────────────────────────────────────────────────
def _render_header(lang: str) -> None:
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        st.title(T("app_title",    lang))
        st.write(T("app_subtitle", lang))
    with col2:
        st.caption(f"📅 {datetime.datetime.now().strftime('%d %b %Y')}")
    st.markdown("---")


# ─────────────────────────────────────────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────────────────────────────────────────
def route_app() -> None:
    """Decide which page to display based on session state."""
    lang = _render_sidebar()
    _render_header(lang)

    if not is_logged_in():
        login_view.render(lang)
    else:
        role = current_role()
        if role == "patient":
            patient_view.render(lang)
        elif role == "doctor":
            doctor_view.render(lang)
        else:
            st.error("Unknown role. Please logout and try again.")


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    route_app()
else:
    # Streamlit runs this module directly, not via __main__
    route_app()
