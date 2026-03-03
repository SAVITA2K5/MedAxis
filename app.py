import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# Local DB layer
from database import (
    init_db,
    get_patient_profile,
    get_doctor_profile,
    get_hospital_info,
    get_vitals_log,
    save_vitals,
    get_dashboard_stats,
)

# -----------------------------------------------------------------------------
# CONFIGURATION & SETUP
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="MedAxis - AI Remote Monitoring",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# DATABASE INIT (runs once per session)
# -----------------------------------------------------------------------------
if 'db_initialized' not in st.session_state:
    with st.spinner("🔌 Connecting to database..."):
        ok = init_db()
    st.session_state['db_initialized'] = ok
    if not ok:
        st.error("⚠️ Could not connect to PostgreSQL. Check your `.streamlit/secrets.toml` credentials.")
        st.stop()

# -----------------------------------------------------------------------------
# MULTILINGUAL SUPPORT (English / Hindi / Tamil)
# -----------------------------------------------------------------------------
translations = {
    "English": {
        "title": "MedAxis",
        "subtitle": "AI-Powered Remote Monitoring System",
        "role_select": "Login As",
        "patient": "Patient",
        "doctor": "Doctor",
        "tab_checkin": "🩺 Health Check-In",
        "tab_profile": "👤 My Profile",
        "tab_hospital": "🏥 Hospital Info",
        "tab_dashboard": "📊 Dashboard",
        "tab_records": "📁 Patient Records",
        "pain_label": "Pain Level (0-10)",
        "sleep_label": "Hours of Sleep",
        "activity_label": "Activity Level",
        "temp_label": "Body Temperature (°F)",
        "submit": "Submit Vitals",
        "risk_score": "Current Risk Assessment",
        "recommendation": "AI Recommendation",
        "welcome": "Welcome back,",
        "connected_to": "Connected to:",
    },
    "Hindi": {
        "title": "MedAxis",
        "subtitle": "एआई रिमोट मॉनिटरिंग सिस्टम",
        "role_select": "लॉगिन करें",
        "patient": "रोगी (Patient)",
        "doctor": "चिकित्सक (Doctor)",
        "tab_checkin": "🩺 स्वास्थ्य चेक-इन",
        "tab_profile": "👤 मेरी प्रोफाइल",
        "tab_hospital": "🏥 अस्पताल की जानकारी",
        "tab_dashboard": "📊 डैशबोर्ड",
        "tab_records": "📁 रोगी रिकॉर्ड",
        "pain_label": "दर्द का स्तर (0-10)",
        "sleep_label": "नींद के घंटे",
        "activity_label": "गतिविधि स्तर",
        "temp_label": "शरीर का तापमान (°F)",
        "submit": "जमा करें",
        "risk_score": "जोखिम मूल्यांकन",
        "recommendation": "सुझाव",
        "welcome": "स्वागत है,",
        "connected_to": "जुड़े हुए हैं:",
    },
    "Tamil": {
        "title": "MedAxis",
        "subtitle": "AI தொலை கண்காணிப்பு அமைப்பு",
        "role_select": "உள்நுழையவும்",
        "patient": "நோயாளி (Patient)",
        "doctor": "மருத்துவர் (Doctor)",
        "tab_checkin": "🩺 உடல்நல பரிசோதனை",
        "tab_profile": "👤 என் சுயவிவரம்",
        "tab_hospital": "🏥 மருத்துவமனை தகவல்",
        "tab_dashboard": "📊 கட்டுப்பாட்டு அறை",
        "tab_records": "📁 நோயாளி பதிவுகள்",
        "pain_label": "வலி நிலை (0-10)",
        "sleep_label": "தூக்க நேரம் (மணி)",
        "activity_label": "செயல்பாடு நிலை",
        "temp_label": "உடல் வெப்பநிலை (°F)",
        "submit": "சமர்ப்பிக்கவும்",
        "risk_score": "இடர் மதிப்பீடு",
        "recommendation": "AI பரிந்துரை",
        "welcome": "வணக்கம்,",
        "connected_to": "இணைக்கப்பட்டுள்ளது:",
    }
}

# -----------------------------------------------------------------------------
# HELPER: PROFILE CARD
# -----------------------------------------------------------------------------
def render_profile_card(title, data: dict):
    """Renders a medical-style ID card using HTML."""
    # Keys to skip (internal DB fields)
    skip_keys = {"hospital_id", "doctor_id", "patient_id", "log_id"}
    content_html = ""
    for key, value in data.items():
        if key in skip_keys or value is None:
            continue
        label = key.replace("_", " ").title()
        content_html += f"<p style='margin: 5px 0;'><b>{label}:</b> <span style='color:#333'>{value}</span></p>"

    st.markdown(f"""
    <div style="
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #0277BD;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    ">
        <h4 style="color: #0277BD; margin-top:0;">{title}</h4>
        <hr style="border: 1px solid #E3F2FD;">
        {content_html}
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# AI LOGIC
# -----------------------------------------------------------------------------
def ai_risk_assessment(pain, sleep, activity, temp):
    """
    Multi-factor weighted risk engine.

    Scoring:
      Pain   : 0-3 → 0pts | 4-6 → 1pt | 7-8 → 2pts | 9-10 → 3pts
      Sleep  : ≥7  → 0pts | 5-6.9 → 1pt | <5 → 2pts
      Temp   : <99.5 → 0pts | 99.5-100.3 → 1pt | ≥100.4 → 3pts (fever = instant High)
      Activity: High → 0pts | Medium → 0pts | Low → 1pt

    Total Score:
      0-1 → Low
      2-3 → Moderate
      4+  → High

    Hard overrides (instant High regardless of score):
      - Pain ≥ 9  (severe pain alone)
      - Temp ≥ 100.4  (fever)
      - Pain ≥ 7 AND sleep < 5  (combined critical)
      - Sleep < 4  (extreme sleep deprivation)
    """
    score = 0
    reasons = []

    # --- Pain scoring ---
    if pain >= 9:
        score += 3
        reasons.append("severe pain")
    elif pain >= 7:
        score += 2
        reasons.append("high pain")
    elif pain >= 4:
        score += 1
        reasons.append("moderate pain")

    # --- Sleep scoring ---
    if sleep < 4:
        score += 3
        reasons.append("extreme sleep deprivation")
    elif sleep < 5:
        score += 2
        reasons.append("very low sleep")
    elif sleep < 7:
        score += 1
        reasons.append("reduced sleep")

    # --- Temperature scoring ---
    if temp >= 100.4:
        score += 3
        reasons.append("fever")
    elif temp >= 99.5:
        score += 1
        reasons.append("elevated temperature")

    # --- Activity scoring ---
    if str(activity) == "Low":
        score += 1
        reasons.append("low activity")

    # --- Hard overrides → always High ---
    hard_override = (
        pain >= 9
        or temp >= 100.4
        or sleep < 4
        or (pain >= 7 and sleep < 5)
    )

    # --- Determine Risk Level ---
    if hard_override or score >= 4:
        risk_score   = "High"
        alert_status = "Urgent"
        if temp >= 100.4:
            message = "🚨 CRITICAL: Fever detected. Possible infection. Seek immediate medical attention."
        elif pain >= 9:
            message = "🚨 CRITICAL: Severe pain reported. Contact your doctor immediately."
        elif sleep < 4:
            message = "🚨 CRITICAL: Extreme sleep deprivation detected. Urgent medical review needed."
        elif pain >= 7 and sleep < 5:
            message = "🚨 CRITICAL: High pain combined with lack of sleep. Contact Doctor immediately."
        else:
            message = f"🚨 HIGH RISK: Multiple danger signals detected ({', '.join(reasons)}). Consult your doctor urgently."

    elif score >= 2:
        risk_score   = "Moderate"
        alert_status = "Monitor"
        message = f"⚠️ WARNING: Elevating symptoms ({', '.join(reasons)}). Rest recommended and monitor closely."

    else:
        risk_score   = "Low"
        alert_status = "Normal"
        message = "✅ Condition looks stable. Maintain current medication and routine."

    return risk_score, message, alert_status


# -----------------------------------------------------------------------------
# CSS STYLING
# -----------------------------------------------------------------------------
st.markdown("""
    <style>
    .stApp { background-color: #f8fcfd; }
    h1, h2, h3, h4 { font-family: 'Segoe UI', sans-serif; color: #0277BD; }

    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
        font-weight: 600;
    }

    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }

    [data-testid="stMetricValue"] { font-size: 2rem !important; color: #0277BD; }

    /* DB status badge */
    .db-badge {
        background: #e8f5e9;
        color: #2e7d32;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# MAIN APP
# -----------------------------------------------------------------------------
def main():
    # --- SIDEBAR ---
    st.sidebar.image("https://img.icons8.com/color/96/caduceus.png", width=80)
    st.sidebar.title("MedAxis")

    # DB status indicator
    st.sidebar.markdown("<span class='db-badge'>🟢 PostgreSQL Connected</span>", unsafe_allow_html=True)
    st.sidebar.markdown("")

    lang_choice = st.sidebar.radio("Language / भाषा / மொழி", ["English", "Hindi", "Tamil"])
    t = translations[lang_choice]

    st.sidebar.markdown("---")
    role = st.sidebar.selectbox(t["role_select"], [t["patient"], t["doctor"]])

    # Load hospital info for sidebar
    hospital_info = get_hospital_info(hospital_id=1)
    st.sidebar.markdown(f"**{t['connected_to']}**")
    st.sidebar.info(f"{hospital_info.get('name', '')} \n\n📞 {hospital_info.get('helpline', '')}")

    # --- HEADER ---
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.title(t["title"])
        st.write(t["subtitle"])
    with col2:
        st.caption(f"📅 {datetime.datetime.now().strftime('%d %b %Y')}")

    st.markdown("---")

    # ==========================
    # PATIENT VIEW
    # ==========================
    if role == t["patient"]:
        patient = get_patient_profile("P-1024")
        p_name  = patient.get("name", "Patient")
        st.subheader(f"{t['welcome']} {p_name}")

        tab1, tab2, tab3 = st.tabs([t["tab_checkin"], t["tab_profile"], t["tab_hospital"]])

        # TAB 1: HEALTH CHECK-IN
        with tab1:
            st.markdown("### 📝 Daily Vitals Entry")
            with st.form("patient_input_form"):
                c1, c2 = st.columns(2)
                with c1:
                    pain     = st.slider(t["pain_label"], 0, 10, 2)
                    activity = st.selectbox(t["activity_label"], ["Low", "Medium", "High"])
                with c2:
                    sleep = st.number_input(t["sleep_label"], 0.0, 24.0, 7.0, 0.5)
                    temp  = st.number_input(t["temp_label"], 90.0, 110.0, 98.6, 0.1)

                submitted = st.form_submit_button(t["submit"], use_container_width=True)

            if submitted:
                risk, msg, alert = ai_risk_assessment(pain, sleep, activity, temp)

                # Show result card
                st.divider()
                st.markdown(f"### {t['risk_score']}")
                res_col1, res_col2 = st.columns([1, 3])
                with res_col1:
                    if risk == "High":
                        st.error(f"## {risk}")
                    elif risk == "Moderate":
                        st.warning(f"## {risk}")
                    else:
                        st.success(f"## {risk}")
                with res_col2:
                    st.info(f"**{t['recommendation']}:** {msg}")

                # 💾 Persist to PostgreSQL
                saved = save_vitals(
                    patient_id=patient.get("patient_id", "P-1024"),
                    name=p_name,
                    pain_level=pain,
                    sleep_hours=sleep,
                    activity=activity,
                    temp=temp,
                    risk=risk,
                    alert=alert,
                    ai_recommendation=msg
                )
                if saved:
                    st.success("✅ Vitals saved to database successfully!")
                else:
                    st.error("❌ Failed to save vitals. Please try again.")

        # TAB 2: PATIENT PROFILE
        with tab2:
            render_profile_card("Patient Medical Profile", patient)
            st.warning("⚠️ To update this information, please contact the hospital administration.")

        # TAB 3: HOSPITAL & DOCTOR INFO
        with tab3:
            doctor   = get_doctor_profile(patient.get("doctor_id", "DOC-889"))
            col_doc, col_hosp = st.columns(2)
            with col_doc:
                render_profile_card("Assigned Specialist", doctor)
            with col_hosp:
                render_profile_card("Hospital Details", hospital_info)

    # ==========================
    # DOCTOR VIEW
    # ==========================
    elif role == t["doctor"]:
        doctor = get_doctor_profile("DOC-889")
        d_name = doctor.get("name", "Doctor")
        st.subheader(f"{t['welcome']} {d_name}")

        tab_dash, tab_recs, tab_doc_prof = st.tabs([
            t["tab_dashboard"], t["tab_records"], t["tab_profile"]
        ])

        # Load data from DB
        vitals = get_vitals_log()
        df = pd.DataFrame(vitals)
        stats = get_dashboard_stats()

        # TAB 1: DASHBOARD
        with tab_dash:
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Total Patients",  stats["total_patients"])
            k2.metric("Active Alerts",   stats["active_alerts"],
                      delta="Needs Action", delta_color="inverse")
            k3.metric("Pending Reviews", stats["pending"])
            k4.metric("Avg Pain Score",  f"{stats['avg_pain']:.1f}")

            st.divider()

            g1, g2 = st.columns([2, 1])
            with g1:
                st.markdown("##### 📈 Pain Trend Analysis")
                if not df.empty:
                    df_sorted = df.sort_values("timestamp")
                    fig = px.area(df_sorted, x="timestamp", y="pain_level",
                                  color="risk", markers=True,
                                  color_discrete_map={"High": "red", "Moderate": "orange", "Low": "green"})
                    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig, use_container_width=True)

            with g2:
                st.markdown("##### ⚠️ Risk Distribution")
                if not df.empty:
                    fig_pie = px.pie(df, names="risk", hole=0.4, color="risk",
                                     color_discrete_map={"High": "#D32F2F",
                                                         "Moderate": "#F57C00",
                                                         "Low": "#388E3C"})
                    fig_pie.update_layout(showlegend=False)
                    st.plotly_chart(fig_pie, use_container_width=True)

        # TAB 2: PATIENT RECORDS
        with tab_recs:
            st.markdown("### 📋 Patient Vitals Log (PostgreSQL)")

            filter_risk = st.multiselect(
                "Filter by Risk Status",
                ["High", "Moderate", "Low"],
                default=["High", "Moderate"]
            )

            if not df.empty:
                filtered_df = df if not filter_risk else df[df['risk'].isin(filter_risk)]
                st.dataframe(
                    filtered_df.sort_values(by="timestamp", ascending=False),
                    column_config={
                        "timestamp":         "Time Recorded",
                        "pain_level":        st.column_config.ProgressColumn(
                                                 "Pain Level", min_value=0, max_value=10, format="%d"),
                        "risk":              st.column_config.TextColumn("AI Risk Score"),
                        "ai_recommendation": st.column_config.TextColumn("AI Recommendation", width="large"),
                    },
                    use_container_width=True,
                    hide_index=True
                )

                # CSV Export
                csv = filtered_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="⬇️ Export Records as CSV",
                    data=csv,
                    file_name=f"medaxis_records_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No records found in database.")

        # TAB 3: DOCTOR PROFILE
        with tab_doc_prof:
            render_profile_card("My Physician Profile", doctor)
            st.info("Your schedule is updated separately in the HMS portal.")


# -----------------------------------------------------------------------------
# ENTRY POINT
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
