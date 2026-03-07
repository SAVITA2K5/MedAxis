"""
components/splash_screen.py
============================
Animated MedAxis splash screen.
Displays for ~2.8 s, then sets session_state['splash_done'] = True and reruns.
"""

import time
import streamlit as st

_SPLASH_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(24px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes pulse {
    0%, 100% { transform: scale(1);    filter: drop-shadow(0 0 12px rgba(255,255,255,0.3)); }
    50%       { transform: scale(1.08); filter: drop-shadow(0 0 28px rgba(255,255,255,0.7)); }
}
@keyframes spin {
    to { transform: rotate(360deg); }
}
@keyframes shimmer {
    0%   { background-position: -400px 0; }
    100% { background-position:  400px 0; }
}

.splash-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 88vh;
    background: linear-gradient(135deg, #012f5c 0%, #0277BD 55%, #01a0e4 100%);
    border-radius: 20px;
    padding: 60px 40px;
    animation: fadeSlideIn 0.7s ease-out forwards;
    font-family: 'Inter', sans-serif;
}
.splash-logo {
    width: 110px;
    animation: pulse 2.2s ease-in-out infinite;
}
.splash-title {
    color: #ffffff;
    font-size: 3.8rem;
    font-weight: 800;
    letter-spacing: -2px;
    margin: 18px 0 0 0;
    text-shadow: 0 3px 16px rgba(0,0,0,0.35);
}
.splash-line {
    width: 70px;
    height: 3px;
    border-radius: 2px;
    background: rgba(255,255,255,0.45);
    margin: 18px 0 16px 0;
}
.splash-tagline {
    color: rgba(255,255,255,0.88);
    font-size: 1.15rem;
    font-weight: 400;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 42px;
}
.splash-spinner {
    width: 38px;
    height: 38px;
    border: 3px solid rgba(255,255,255,0.25);
    border-top-color: #ffffff;
    border-radius: 50%;
    animation: spin 0.85s linear infinite;
    margin-bottom: 14px;
}
.splash-loading-text {
    color: rgba(255,255,255,0.65);
    font-size: 0.82rem;
    letter-spacing: 2.5px;
    text-transform: uppercase;
}
</style>
"""


def show(tagline: str = "Smart Healthcare Intelligence",
         loading_text: str = "Initializing secure connection...",
         duration: float = 2.8) -> None:
    """
    Render the splash screen, sleep for `duration` seconds,
    then mark splash as done and trigger a rerun.
    """
    st.markdown(_SPLASH_CSS, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="splash-wrap">
        <img class="splash-logo"
             src="https://img.icons8.com/color/120/caduceus.png"
             alt="MedAxis logo"/>
        <div class="splash-title">MedAxis</div>
        <div class="splash-line"></div>
        <div class="splash-tagline">{tagline}</div>
        <div class="splash-spinner"></div>
        <div class="splash-loading-text">{loading_text}</div>
    </div>
    """, unsafe_allow_html=True)

    time.sleep(duration)
    st.session_state["splash_done"] = True
    st.rerun()
