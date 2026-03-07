"""
auth.py
=======
MedAxis authentication helpers.

In production, replace plain-text dicts with bcrypt-hashed DB lookups.
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Demo credentials  — swap for hashed DB lookup in production
# ---------------------------------------------------------------------------
_PATIENT_CREDS: dict[str, str] = {
    "P-1024": "patient123",
}

_DOCTOR_CREDS: dict[str, str] = {
    "DOC-889": "doctor123",
}


def validate_patient(pid: str, pwd: str) -> bool:
    """Return True if patient credentials are valid."""
    return _PATIENT_CREDS.get(pid.strip()) == pwd


def validate_doctor(did: str, pwd: str) -> bool:
    """Return True if doctor credentials are valid."""
    return _DOCTOR_CREDS.get(did.strip()) == pwd


def login_patient(pid: str) -> None:
    """Store patient session variables."""
    st.session_state["logged_in"] = True
    st.session_state["role"]      = "patient"
    st.session_state["user_id"]   = pid.strip()


def login_doctor(did: str) -> None:
    """Store doctor session variables."""
    st.session_state["logged_in"] = True
    st.session_state["role"]      = "doctor"
    st.session_state["user_id"]   = did.strip()


def logout() -> None:
    """Clear all auth-related session state."""
    for key in ["logged_in", "role", "user_id", "login_screen"]:
        st.session_state.pop(key, None)


def is_logged_in() -> bool:
    return bool(st.session_state.get("logged_in"))


def current_role() -> str | None:
    return st.session_state.get("role")
