import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import random

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
# SESSION STATE & DATA INITIALIZATION
# -----------------------------------------------------------------------------
if 'patient_data' not in st.session_state:
    # Historical Data
    st.session_state['patient_data'] = [
        {"timestamp": datetime.datetime.now() - datetime.timedelta(days=1), "patient_id": "P-1024", "name": "Rajesh Kumar", "pain_level": 3, "sleep_hours": 7.5, "activity": "Medium", "temp": 98.6, "risk": "Low", "alert": "Normal"},
        {"timestamp": datetime.datetime.now() - datetime.timedelta(hours=5), "patient_id": "P-1024", "name": "Rajesh Kumar", "pain_level": 8, "sleep_hours": 4.0, "activity": "Low", "temp": 99.1, "risk": "High", "alert": "Urgent"},
        {"timestamp": datetime.datetime.now() - datetime.timedelta(days=2), "patient_id": "P-1024", "name": "Rajesh Kumar", "pain_level": 5, "sleep_hours": 6.0, "activity": "Low", "temp": 98.4, "risk": "Moderate", "alert": "Monitor"},
    ]

# Patient Profile (Mock Data)
if 'patient_profile' not in st.session_state:
    st.session_state['patient_profile'] = {
        "name": "Rajesh Kumar",
        "id": "P-1024",
        "age": 45,
        "blood_group": "O+",
        "condition": "Chronic Arthritis",
        "contact": "+91-9876543210",
        "address": "12/A, Green Park, New Delhi"
    }

# Doctor Profile (Mock Data)
if 'doctor_profile' not in st.session_state:
    st.session_state['doctor_profile'] = {
        "name": "Dr. Ananya Singh",
        "id": "DOC-889",
        "specialty": "Rheumatology & Pain Management",
        "qualification": "MBBS, MD (Ortho)",
        "contact": "+91-11-45678900",
        "email": "dr.ananya@medaxis.com"
    }

# Hospital Details
if 'hospital_info' not in st.session_state:
    st.session_state['hospital_info'] = {
        "name": "City Care Specialty Hospital",
        "branch": "South Wing, Bangalore",
        "helpline": "1800-MED-AXIS",
        "website": "www.citycarehospital.com"
    }

# -----------------------------------------------------------------------------
# MULTILINGUAL SUPPORT (English / Hindi)
# -----------------------------------------------------------------------------
translations = {
    "English": {
        "title": "MedAxis",
        "subtitle": "AI-Powered Remote Monitoring System",
        "role_select": "Login As",
        "patient": "Patient",
        "doctor": "Doctor",
        # Tabs
        "tab_checkin": "🩺 Health Check-In",
        "tab_profile": "👤 My Profile",
        "tab_hospital": "🏥 Hospital Info",
        "tab_dashboard": "📊 Dashboard",
        "tab_records": "📁 Patient Records",
        # Labels
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
        "patient_dash": "रोगी स्वास्थ्य चेक-इन",
        "doctor_dash": "क्लीनिशियन डैशबोर्ड",
        # Tabs
        "tab_checkin": "🩺 स्वास्थ्य चेक-इन",
        "tab_profile": "👤 मेरी प्रोफाइल",
        "tab_hospital": "🏥 अस्पताल की जानकारी",
        "tab_dashboard": "📊 डैशबोर्ड",
        "tab_records": "📁 रोगी रिकॉर्ड",
        # Labels
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
        # Tabs
        "tab_checkin": "🩺 உடல்நல பரிசோதனை",
        "tab_profile": "👤 என் சுயவிவரம்",
        "tab_hospital": "🏥 மருத்துவமனை தகவல்",
        "tab_dashboard": "📊 கட்டுப்பாட்டு அறை",
        "tab_records": "📁 நோயாளி பதிவுகள்",
        # Labels
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
def render_profile_card(title, data):
    """Renders a medical-style ID card using HTML"""
    content_html = ""
    for key, value in data.items():
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
    """simulate AI risk score"""
    risk_score = "Low"
    message = "Condition looks stable. Maintain current medication."
    alert_status = "Normal"

    if pain >= 7 and sleep < 5:
        risk_score = "High"
        message = "CRITICAL: Combined high pain & lack of sleep. Contact Doctor immediately."
        alert_status = "Urgent"
    elif temp > 100.4:
        risk_score = "High"
        message = "ALERT: Fever detected. Possible infection."
        alert_status = "Urgent"
    elif (pain >= 4) or (str(activity) == "Low" and pain > 2):
        risk_score = "Moderate"
        message = "WARNING: Elevating symptoms. Rest recommended."
        alert_status = "Monitor"

    return risk_score, message, alert_status

# -----------------------------------------------------------------------------
# CSS styling
# -----------------------------------------------------------------------------
st.markdown("""
    <style>
    .stApp { background-color: #f8fcfd; }
    h1, h2, h3, h4 { font-family: 'Segoe UI', sans-serif; color: #0277BD; }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] { font-size: 2rem !important; color: #0277BD; }
    </style>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MAIN APP
# -----------------------------------------------------------------------------
def main():
    # --- SIDEBAR CONFIG ---
    st.sidebar.image("https://img.icons8.com/color/96/caduceus.png", width=80) 
    st.sidebar.title("MedAxis")
    lang_choice = st.sidebar.radio("Language / भाषा / மொழி", ["English", "Hindi", "Tamil"])
    t = translations[lang_choice]
    
    st.sidebar.markdown("---")
    role = st.sidebar.selectbox(t["role_select"], [t["patient"], t["doctor"]])
    
    # Hospital Info Widget in Sidebar
    st.sidebar.markdown(f"**{t['connected_to']}**")
    st.sidebar.info(f"{st.session_state['hospital_info']['name']}\n\n📞 {st.session_state['hospital_info']['helpline']}")

    # --- HEADER ---
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.title(t["title"])
        st.write(t["subtitle"])
    with col2:
        # Date display
        st.caption(f"📅 {datetime.datetime.now().strftime('%d %b %Y')}")

    st.markdown("---")

    # ==========================
    # PATIENT VIEW
    # ==========================
    if role == t["patient"]:
        p_name = st.session_state['patient_profile']['name']
        st.subheader(f"{t['welcome']} {p_name}")
        
        # Tabs for better organization
        tab1, tab2, tab3 = st.tabs([t["tab_checkin"], t["tab_profile"], t["tab_hospital"]])
        
        # TAB 1: HEALTH CHECK-IN
        with tab1:
            with st.container():
                st.markdown("### 📝 Daily Vitals Entry")
                with st.form("patient_input_form"):
                    c1, c2 = st.columns(2)
                    with c1:
                        pain = st.slider(t["pain_label"], 0, 10, 2)
                        activity = st.selectbox(t["activity_label"], ["Low", "Medium", "High"])
                    with c2:
                        sleep = st.number_input(t["sleep_label"], 0.0, 24.0, 7.0, 0.5)
                        temp = st.number_input(t["temp_label"], 90.0, 110.0, 98.6, 0.1)
                    
                    submitted = st.form_submit_button(t["submit"], use_container_width=True)

                if submitted:
                    risk, msg, alert = ai_risk_assessment(pain, sleep, activity, temp)
                    
                    # Display Result Card
                    st.divider()
                    st.markdown(f"### {t['risk_score']}")
                    
                    res_col1, res_col2 = st.columns([1,3])
                    with res_col1:
                        if risk == "High":
                            st.error(f"## {risk}")
                        elif risk == "Moderate":
                            st.warning(f"## {risk}")
                        else:
                            st.success(f"## {risk}")
                    
                    with res_col2:
                        st.info(f"**{t['recommendation']}:** {msg}")

                    # Save Data
                    new_entry = {
                        "timestamp": datetime.datetime.now(),
                        "patient_id": st.session_state['patient_profile']['id'],
                        "name": p_name,
                        "pain_level": pain,
                        "sleep_hours": sleep,
                        "activity": activity,
                        "temp": temp,
                        "risk": risk,
                        "alert": alert
                    }
                    st.session_state['patient_data'].append(new_entry)
        
        # TAB 2: PATIENT PROFILE
        with tab2:
            render_profile_card("Patient Medical Profile", st.session_state['patient_profile'])
            st.warning("⚠️ To update this information, please contact the hospital administration.")

        # TAB 3: HOSPITAL & DOCTOR INFO
        with tab3:
            col_doc, col_hosp = st.columns(2)
            with col_doc:
                render_profile_card("Assigned Specialist", st.session_state['doctor_profile'])
            with col_hosp:
                render_profile_card("Hospital Details", st.session_state['hospital_info'])

    # ==========================
    # DOCTOR VIEW
    # ==========================
    elif role == t["doctor"]:
        d_name = st.session_state['doctor_profile']['name']
        st.subheader(f"{t['welcome']} {d_name}")
        
        tab_dash, tab_recs, tab_doc_prof = st.tabs([t["tab_dashboard"], t["tab_records"], t["tab_profile"]])

        df = pd.DataFrame(st.session_state['patient_data'])

        # TAB 1: DASHBOARD
        with tab_dash:
            # KPIS
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Total Patients", "142") # Simulated total
            k2.metric("Active Alerts", len(df[df['risk']=='High']), delta="Needs Action", delta_color="inverse")
            k3.metric("Pending Reviews", "5")
            k4.metric("Avg Pain Score", f"{df['pain_level'].mean():.1f}")
            
            st.divider()
            
            # Charts
            g1, g2 = st.columns([2,1])
            with g1:
                st.markdown("##### 📈 Pain Trend Analysis (Last 7 Days)")
                if not df.empty:
                    df_sorted = df.sort_values("timestamp")
                    fig = px.area(df_sorted, x="timestamp", y="pain_level", color="risk", markers=True,
                                  color_discrete_map={"High":"red", "Moderate":"orange", "Low":"green"})
                    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig, use_container_width=True)
            
            with g2:
                st.markdown("##### ⚠️ Risk Distribution")
                if not df.empty:
                    fig_pie = px.pie(df, names="risk", hole=0.4,
                                     color="risk",
                                     color_discrete_map={"High":"#D32F2F", "Moderate":"#F57C00", "Low":"#388E3C"})
                    fig_pie.update_layout(showlegend=False)
                    st.plotly_chart(fig_pie, use_container_width=True)

        # TAB 2: DETAILED RECORDS
        with tab_recs:
            st.markdown("### Patient Logs Database")
            
            # Simple Filter
            filter_risk = st.multiselect("Filter by Risk Status", ["High", "Moderate", "Low"], default=["High", "Moderate"])
            
            if not df.empty:
                filtered_df = df if not filter_risk else df[df['risk'].isin(filter_risk)]
                
                # Custom Styling for Table
                st.dataframe(
                    filtered_df.sort_values(by="timestamp", ascending=False),
                    column_config={
                        "timestamp": "Time Recorded",
                        "pain_level": st.column_config.ProgressColumn("Pain Level", min_value=0, max_value=10, format="%d"),
                        "risk": st.column_config.TextColumn("AI Risk Score"),
                    },
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No records found.")
        
        # TAB 3: DOCTOR PROFILE
        with tab_doc_prof:
            render_profile_card("My Physician Profile", st.session_state['doctor_profile'])
            st.info("Your schedule is updated separately in the HMS portal.")

# -----------------------------------------------------------------------------
# ENTRY POINT
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
