# MedAxis – AI-Based Remote Pain Management & Clinical Decision Support Platform

MedAxis is a healthcare technology prototype that enables predictive remote monitoring of chronic pain patients through AI-driven risk assessment and clinician decision support. The platform helps shift pain management from reactive treatment to proactive intervention by identifying potential pain flare-ups before they escalate.

## Problem Statement

Chronic pain affects millions of patients worldwide and is often managed only after symptoms worsen. Limited monitoring between hospital visits can lead to delayed intervention, increased healthcare costs, and over-reliance on opioid-based treatments. Additionally, elderly and non-English-speaking populations face accessibility challenges when using digital healthcare solutions.

## Solution

MedAxis provides a multilingual digital healthcare platform that:

- Collects patient health data such as pain levels, sleep duration, and activity metrics.
- Uses predictive logic to generate risk scores and identify potential pain flare-ups.
- Provides clinicians with dashboards, trend analytics, and intelligent alerts.
- Supports proactive, non-opioid intervention strategies.
- Improves accessibility through multilingual support.

## Key Features

- Patient Health Monitoring
- AI-Based Risk Prediction Engine
- Doctor & Patient Dashboards
- Real-Time Alerts & Notifications
- Pain Trend Visualization
- Multilingual Support (English, Tamil, Hindi)
- PostgreSQL Database Integration
- Cloud Deployment Support

## Technology Stack

| Component | Technology |
|------------|------------|
| Frontend | Streamlit |
| Backend | Python |
| Database | PostgreSQL |
| Data Processing | Pandas |
| Visualization | Plotly |
| Version Control | Git & GitHub |
| Deployment | Render |

## System Workflow

1. Patient enters health parameters through the application.
2. The AI risk engine analyzes pain-related indicators.
3. Risk scores are generated based on patient data.
4. Alerts are triggered for high-risk cases.
5. Doctors access dashboards to review trends and patient status.
6. Early intervention recommendations can be provided.

## Installation

### Clone Repository

```bash
git clone https://github.com/SAVITA2K5/MedAxis.git
cd MedAxis
```

### Create Virtual Environment

```bash
python -m venv venv
```

Activate environment:

Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Application

```bash
streamlit run app.py
```

## Project Impact

- Encourages proactive healthcare management
- Supports non-opioid pain intervention strategies
- Improves clinician efficiency through decision support
- Enhances healthcare accessibility through multilingual design
- Reduces monitoring gaps between hospital visits

## Future Scope

- Integration with wearable health devices
- Advanced machine learning models
- Electronic Health Record (EHR) integration
- Telemedicine support
- Expansion to cardiac care and diabetes monitoring
- Mobile application development using Flutter or React Native

## Disclaimer

MedAxis is a proof-of-concept healthcare prototype developed for educational, research, and startup validation purposes. It does not provide medical diagnosis, treatment, or clinical recommendations and should not be used as a substitute for professional medical advice.

## Team

**Team Name:** MedAxis

- Savita S
- Srihitha Y

## Repository

GitHub: https://github.com/SAVITA2K5/MedAxis

---

**MedAxis – Don't Just Track Pain. Predict It.**
