CREATE DATABASE medaxis_db;
-- =============================================
-- MedAxis: Table Creation
-- =============================================

CREATE TABLE IF NOT EXISTS hospitals (
    hospital_id  SERIAL PRIMARY KEY,
    name         VARCHAR(150) NOT NULL,
    branch       VARCHAR(150),
    helpline     VARCHAR(50),
    website      VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS doctors (
    doctor_id      VARCHAR(20) PRIMARY KEY,
    name           VARCHAR(100) NOT NULL,
    specialty      VARCHAR(100),
    qualification  VARCHAR(100),
    contact        VARCHAR(50),
    email          VARCHAR(100),
    hospital_id    INTEGER REFERENCES hospitals(hospital_id)
);

CREATE TABLE IF NOT EXISTS patients (
    patient_id   VARCHAR(20) PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    age          INTEGER,
    blood_group  VARCHAR(10),
    condition    VARCHAR(200),
    contact      VARCHAR(50),
    address      TEXT,
    doctor_id    VARCHAR(20) REFERENCES doctors(doctor_id)
);

CREATE TABLE IF NOT EXISTS vitals_log (
    log_id             SERIAL PRIMARY KEY,
    patient_id         VARCHAR(20) NOT NULL,
    name               VARCHAR(100),
    timestamp          TIMESTAMP DEFAULT NOW(),
    pain_level         INTEGER,
    sleep_hours        FLOAT,
    activity           VARCHAR(20),
    temp               FLOAT,
    risk               VARCHAR(20),
    alert              VARCHAR(20),
    ai_recommendation  TEXT
);

-- =============================================
-- MedAxis: Seed Demo Data
-- =============================================

INSERT INTO hospitals (name, branch, helpline, website)
VALUES ('City Care Specialty Hospital', 'South Wing, Bangalore', '1800-MED-AXIS', 'www.citycarehospital.com');

INSERT INTO doctors (doctor_id, name, specialty, qualification, contact, email, hospital_id)
VALUES ('DOC-889', 'Dr. Ananya Singh', 'Rheumatology & Pain Management', 'MBBS, MD (Ortho)', '+91-11-45678900', 'dr.ananya@medaxis.com', 1);

INSERT INTO patients (patient_id, name, age, blood_group, condition, contact, address, doctor_id)
VALUES ('P-1024', 'Rajesh Kumar', 45, 'O+', 'Chronic Arthritis', '+91-9876543210', '12/A, Green Park, New Delhi', 'DOC-889');

INSERT INTO vitals_log (patient_id, name, timestamp, pain_level, sleep_hours, activity, temp, risk, alert, ai_recommendation)
VALUES
    ('P-1024', 'Rajesh Kumar', NOW() - INTERVAL '2 days', 5, 6.0, 'Low',  98.4, 'Moderate', 'Monitor', 'WARNING: Elevating symptoms. Rest recommended.'),
    ('P-1024', 'Rajesh Kumar', NOW() - INTERVAL '1 day',  3, 7.5, 'Medium', 98.6, 'Low', 'Normal', 'Condition looks stable. Maintain current medication.'),
    ('P-1024', 'Rajesh Kumar', NOW() - INTERVAL '5 hours', 8, 4.0, 'Low', 99.1, 'High', 'Urgent', 'CRITICAL: Combined high pain & lack of sleep. Contact Doctor immediately.');
SELECT * FROM hospitals;
SELECT * FROM doctors;
SELECT * FROM patients;
SELECT * FROM vitals_log;