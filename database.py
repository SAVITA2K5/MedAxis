"""
database.py — MedAxis PostgreSQL Database Layer
================================================
Handles all database connections, schema definitions,
and CRUD operations using SQLAlchemy Core.
"""

import streamlit as st
from urllib.parse import quote_plus
from sqlalchemy import (
    create_engine, text, MetaData, Table, Column,
    Integer, Float, String, DateTime, Text
)
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime


# -----------------------------------------------------------------------------
# ENGINE — reads credentials from .streamlit/secrets.toml
# -----------------------------------------------------------------------------
@st.cache_resource
def get_engine():
    """Create and return a cached SQLAlchemy engine."""
    try:
        password = quote_plus(st.secrets['db']['password'])  # safely encode special chars like @
        db_url = (
            f"postgresql+psycopg2://"
            f"{st.secrets['db']['user']}:{password}"
            f"@{st.secrets['db']['host']}:{st.secrets['db']['port']}"
            f"/{st.secrets['db']['name']}"
        )
        engine = create_engine(db_url, pool_pre_ping=True, pool_size=5, max_overflow=10)
        return engine
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        return None


# -----------------------------------------------------------------------------
# SCHEMA — Table Definitions
# -----------------------------------------------------------------------------
metadata = MetaData()

hospitals_table = Table("hospitals", metadata,
    Column("hospital_id",   Integer,  primary_key=True, autoincrement=True),
    Column("name",          String(150), nullable=False),
    Column("branch",        String(150)),
    Column("helpline",      String(50)),
    Column("website",       String(100)),
)

doctors_table = Table("doctors", metadata,
    Column("doctor_id",     String(20),  primary_key=True),
    Column("name",          String(100), nullable=False),
    Column("specialty",     String(100)),
    Column("qualification", String(100)),
    Column("contact",       String(50)),
    Column("email",         String(100)),
    Column("hospital_id",   Integer),   # FK → hospitals
)

patients_table = Table("patients", metadata,
    Column("patient_id",   String(20),  primary_key=True),
    Column("name",         String(100), nullable=False),
    Column("age",          Integer),
    Column("blood_group",  String(10)),
    Column("condition",    String(200)),
    Column("contact",      String(50)),
    Column("address",      Text),
    Column("doctor_id",    String(20)), # FK → doctors
)

vitals_log_table = Table("vitals_log", metadata,
    Column("log_id",            Integer,  primary_key=True, autoincrement=True),
    Column("patient_id",        String(20), nullable=False),
    Column("name",              String(100)),
    Column("timestamp",         DateTime, default=datetime.now),
    Column("pain_level",        Integer),
    Column("sleep_hours",       Float),
    Column("activity",          String(20)),
    Column("temp",              Float),
    Column("risk",              String(20)),
    Column("alert",             String(20)),
    Column("ai_recommendation", Text),
)


# -----------------------------------------------------------------------------
# INIT — Create Tables if They Don't Exist
# -----------------------------------------------------------------------------
def init_db():
    """Create all tables and seed default data if empty."""
    engine = get_engine()
    if engine is None:
        return False
    try:
        metadata.create_all(engine)
        _seed_default_data(engine)
        return True
    except SQLAlchemyError as e:
        st.error(f"❌ Database initialization error: {e}")
        return False


def _seed_default_data(engine):
    """Insert demo hospital, doctor, patient, and vitals if tables are empty."""
    with engine.begin() as conn:
        # Seed Hospital
        existing = conn.execute(text("SELECT COUNT(*) FROM hospitals")).scalar()
        if existing == 0:
            conn.execute(hospitals_table.insert().values(
                name="City Care Specialty Hospital",
                branch="South Wing, Bangalore",
                helpline="1800-MED-AXIS",
                website="www.citycarehospital.com"
            ))

        # Seed Doctor
        existing = conn.execute(text("SELECT COUNT(*) FROM doctors")).scalar()
        if existing == 0:
            conn.execute(doctors_table.insert().values(
                doctor_id="DOC-889",
                name="Dr. Ananya Singh",
                specialty="Rheumatology & Pain Management",
                qualification="MBBS, MD (Ortho)",
                contact="+91-11-45678900",
                email="dr.ananya@medaxis.com",
                hospital_id=1
            ))

        # Seed Patient
        existing = conn.execute(text("SELECT COUNT(*) FROM patients")).scalar()
        if existing == 0:
            conn.execute(patients_table.insert().values(
                patient_id="P-1024",
                name="Rajesh Kumar",
                age=45,
                blood_group="O+",
                condition="Chronic Arthritis",
                contact="+91-9876543210",
                address="12/A, Green Park, New Delhi",
                doctor_id="DOC-889"
            ))

        # Seed historical vitals
        existing = conn.execute(text("SELECT COUNT(*) FROM vitals_log")).scalar()
        if existing == 0:
            from datetime import timedelta
            sample_vitals = [
                dict(patient_id="P-1024", name="Rajesh Kumar",
                     timestamp=datetime.now() - timedelta(days=2),
                     pain_level=5, sleep_hours=6.0, activity="Low",
                     temp=98.4, risk="Moderate", alert="Monitor",
                     ai_recommendation="WARNING: Elevating symptoms. Rest recommended."),
                dict(patient_id="P-1024", name="Rajesh Kumar",
                     timestamp=datetime.now() - timedelta(days=1),
                     pain_level=3, sleep_hours=7.5, activity="Medium",
                     temp=98.6, risk="Low", alert="Normal",
                     ai_recommendation="Condition looks stable. Maintain current medication."),
                dict(patient_id="P-1024", name="Rajesh Kumar",
                     timestamp=datetime.now() - timedelta(hours=5),
                     pain_level=8, sleep_hours=4.0, activity="Low",
                     temp=99.1, risk="High", alert="Urgent",
                     ai_recommendation="CRITICAL: Combined high pain & lack of sleep. Contact Doctor immediately."),
            ]
            conn.execute(vitals_log_table.insert(), sample_vitals)


# -----------------------------------------------------------------------------
# READ OPERATIONS
# -----------------------------------------------------------------------------
def get_patient_profile(patient_id: str) -> dict:
    engine = get_engine()
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT * FROM patients WHERE patient_id = :pid"),
            {"pid": patient_id}
        ).mappings().fetchone()
        return dict(row) if row else {}


def get_doctor_profile(doctor_id: str) -> dict:
    engine = get_engine()
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT * FROM doctors WHERE doctor_id = :did"),
            {"did": doctor_id}
        ).mappings().fetchone()
        return dict(row) if row else {}


def get_hospital_info(hospital_id: int = 1) -> dict:
    engine = get_engine()
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT * FROM hospitals WHERE hospital_id = :hid"),
            {"hid": hospital_id}
        ).mappings().fetchone()
        return dict(row) if row else {}


def get_vitals_log(patient_id: str = None) -> list:
    """Fetch all vitals, optionally filtered by patient_id."""
    engine = get_engine()
    with engine.connect() as conn:
        if patient_id:
            rows = conn.execute(
                text("SELECT * FROM vitals_log WHERE patient_id = :pid ORDER BY timestamp DESC"),
                {"pid": patient_id}
            ).mappings().fetchall()
        else:
            rows = conn.execute(
                text("SELECT * FROM vitals_log ORDER BY timestamp DESC")
            ).mappings().fetchall()
        return [dict(r) for r in rows]


# -----------------------------------------------------------------------------
# WRITE OPERATIONS
# -----------------------------------------------------------------------------
def save_vitals(patient_id: str, name: str, pain_level: int, sleep_hours: float,
                activity: str, temp: float, risk: str, alert: str,
                ai_recommendation: str) -> bool:
    """Insert a new vitals record into vitals_log."""
    engine = get_engine()
    try:
        with engine.begin() as conn:
            conn.execute(vitals_log_table.insert().values(
                patient_id=patient_id,
                name=name,
                timestamp=datetime.now(),
                pain_level=pain_level,
                sleep_hours=sleep_hours,
                activity=activity,
                temp=temp,
                risk=risk,
                alert=alert,
                ai_recommendation=ai_recommendation
            ))
        return True
    except SQLAlchemyError as e:
        st.error(f"❌ Failed to save vitals: {e}")
        return False


def get_dashboard_stats() -> dict:
    """Aggregate stats for the Doctor Dashboard KPIs."""
    engine = get_engine()
    with engine.connect() as conn:
        total_patients = conn.execute(text("SELECT COUNT(*) FROM patients")).scalar()
        active_alerts  = conn.execute(text("SELECT COUNT(*) FROM vitals_log WHERE risk = 'High'")).scalar()
        avg_pain       = conn.execute(text("SELECT AVG(pain_level) FROM vitals_log")).scalar()
        pending        = conn.execute(text("SELECT COUNT(*) FROM vitals_log WHERE alert = 'Monitor'")).scalar()
    return {
        "total_patients": total_patients or 0,
        "active_alerts":  active_alerts  or 0,
        "avg_pain":       round(float(avg_pain), 1) if avg_pain else 0.0,
        "pending":        pending or 0,
    }
