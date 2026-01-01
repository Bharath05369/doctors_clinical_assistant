# complete_clinical_chatbot.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import sqlite3
import os
import re
from typing import Dict, List, Optional
import random

# ============================================
# 1. COMPLETE DATABASE CREATION WITH ALL DATA
# ============================================
def create_complete_database():
    """Create a fully populated clinical database"""
    
    # Remove old database if exists
    if os.path.exists('complete_clinical.db'):
        os.remove('complete_clinical.db')
    
    conn = sqlite3.connect('complete_clinical.db')
    
    # ============================================
    # CREATE ALL TABLES
    # ============================================
    
    # Patients table
    conn.execute('''
    CREATE TABLE patients (
        patient_id TEXT PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        date_of_birth DATE,
        age INTEGER,
        gender TEXT,
        primary_diagnosis TEXT,
        secondary_diagnosis TEXT,
        allergies TEXT,
        primary_physician TEXT,
        last_visit DATE,
        next_appointment DATE,
        emergency_contact TEXT
    )
    ''')
    
    # Lab results table
    conn.execute('''
    CREATE TABLE lab_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT,
        result_date DATE,
        test_name TEXT,
        value REAL,
        unit TEXT,
        reference_low REAL,
        reference_high REAL,
        interpretation TEXT,
        lab_name TEXT
    )
    ''')
    
    # Vital signs table
    conn.execute('''
    CREATE TABLE vital_signs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT,
        measurement_date DATE,
        systolic_bp INTEGER,
        diastolic_bp INTEGER,
        heart_rate INTEGER,
        temperature REAL,
        respiratory_rate INTEGER,
        oxygen_saturation INTEGER,
        weight_kg REAL,
        height_cm REAL,
        bmi REAL
    )
    ''')
    
    # Medications table
    conn.execute('''
    CREATE TABLE medications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT,
        medication_name TEXT,
        generic_name TEXT,
        dosage TEXT,
        frequency TEXT,
        route TEXT,
        start_date DATE,
        end_date DATE,
        status TEXT,
        prescribing_physician TEXT,
        pharmacy TEXT
    )
    ''')
    
    # Clinical notes table
    conn.execute('''
    CREATE TABLE clinical_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT,
        note_date DATE,
        note_type TEXT,
        title TEXT,
        content TEXT,
        physician TEXT
    )
    ''')
    
    # ============================================
    # INSERT PATIENTS
    # ============================================
    
    patients = [
        # Patient 1: Diabetes + Hypertension
        ('P001', 'John', 'Doe', '1965-03-15', 58, 'M',
         'Type 2 Diabetes Mellitus', 'Hypertension, Hyperlipidemia',
         'Penicillin, Sulfa drugs', 'Dr. Sarah Chen', '2024-01-15', '2024-04-15',
         'Jane Doe (555-0123)'),
        
        # Patient 2: Hypertension only
        ('P002', 'Jane', 'Smith', '1978-11-30', 45, 'F',
         'Essential Hypertension', 'GERD, Osteoarthritis',
         'None known', 'Dr. Amanda Lee', '2024-01-10', '2024-03-10',
         'John Smith (555-0124)'),
        
        # Patient 3: Coronary Artery Disease
        ('P003', 'Robert', 'Johnson', '1958-07-22', 65, 'M',
         'Coronary Artery Disease', 'Atrial Fibrillation, COPD',
         'Iodine contrast', 'Dr. Michael Rodriguez', '2024-01-20', '2024-02-20',
         'Mary Johnson (555-0125)'),
        
        # Patient 4: Asthma/COPD
        ('P004', 'Maria', 'Garcia', '1985-05-10', 38, 'F',
         'Asthma with COPD overlap', 'Anxiety, Obesity',
         'Aspirin', 'Dr. James Wilson', '2024-01-25', '2024-04-25',
         'Carlos Garcia (555-0126)'),
        
        # Patient 5: Renal Disease
        ('P005', 'David', 'Brown', '1972-09-18', 51, 'M',
         'Chronic Kidney Disease Stage 3', 'Diabetes, Hypertension',
         'NSAIDs', 'Dr. Sarah Chen', '2024-01-18', '2024-03-18',
         'Linda Brown (555-0127)'),
    ]
    
    for patient in patients:
        conn.execute('''
        INSERT INTO patients VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        ''', patient)
    
    # ============================================
    # INSERT LAB RESULTS (HbA1c, Glucose, Cholesterol, etc.)
    # ============================================
    
    # Lab test definitions
    lab_tests = {
        'HbA1c': {'unit': '%', 'low': 4.0, 'high': 5.6},
        'Fasting Glucose': {'unit': 'mg/dL', 'low': 70, 'high': 100},
        'Random Glucose': {'unit': 'mg/dL', 'low': 70, 'high': 140},
        'LDL Cholesterol': {'unit': 'mg/dL', 'low': 0, 'high': 100},
        'HDL Cholesterol': {'unit': 'mg/dL', 'low': 40, 'high': 60},
        'Triglycerides': {'unit': 'mg/dL', 'low': 0, 'high': 150},
        'Creatinine': {'unit': 'mg/dL', 'low': 0.6, 'high': 1.2},
        'eGFR': {'unit': 'mL/min', 'low': 90, 'high': 120},
        'ALT': {'unit': 'U/L', 'low': 7, 'high': 56},
        'AST': {'unit': 'U/L', 'low': 5, 'high': 40},
        'Total Bilirubin': {'unit': 'mg/dL', 'low': 0.1, 'high': 1.2},
        'WBC': {'unit': 'K/uL', 'low': 4.5, 'high': 11.0},
        'Hemoglobin': {'unit': 'g/dL', 'low': 13.5, 'high': 17.5},
        'Hematocrit': {'unit': '%', 'low': 38.8, 'high': 50.0},
        'Platelets': {'unit': 'K/uL', 'low': 150, 'high': 450},
    }
    
    # Generate lab data for each patient
    for patient_id in ['P001', 'P002', 'P003', 'P004', 'P005']:
        # Different test sets based on patient condition
        if patient_id == 'P001':  # Diabetic
            patient_tests = ['HbA1c', 'Fasting Glucose', 'LDL Cholesterol', 'HDL Cholesterol', 
                           'Triglycerides', 'Creatinine', 'ALT']
        elif patient_id == 'P002':  # Hypertensive
            patient_tests = ['Fasting Glucose', 'LDL Cholesterol', 'HDL Cholesterol', 
                           'Triglycerides', 'Creatinine', 'ALT']
        elif patient_id == 'P003':  # Cardiac
            patient_tests = ['LDL Cholesterol', 'HDL Cholesterol', 'Triglycerides', 
                           'Creatinine', 'ALT', 'AST']
        elif patient_id == 'P004':  # Asthma
            patient_tests = ['WBC', 'Hemoglobin', 'Hematocrit', 'ALT', 'AST']
        else:  # Renal
            patient_tests = ['Creatinine', 'eGFR', 'Hemoglobin', 'Hematocrit', 'Platelets']
        
        # Generate 12 months of data
        for month in range(12):
            date = (datetime(2023, 1, 15) + timedelta(days=30*month)).strftime('%Y-%m-%d')
            
            for test_name in patient_tests:
                test_info = lab_tests[test_name]
                
                # Patient-specific patterns
                if patient_id == 'P001' and test_name == 'HbA1c':
                    # Improving trend for diabetic patient
                    value = round(8.5 - (month * 0.2) + random.uniform(-0.1, 0.1), 1)
                elif patient_id == 'P001' and test_name == 'Fasting Glucose':
                    value = round(145 - (month * 3) + random.uniform(-10, 10), 0)
                elif patient_id == 'P003' and test_name == 'LDL Cholesterol':
                    # Improving with treatment
                    value = round(110 - (month * 2) + random.uniform(-5, 5), 0)
                elif patient_id == 'P005' and test_name == 'Creatinine':
                    # Stable but elevated for renal patient
                    value = round(1.8 + random.uniform(-0.1, 0.1), 1)
                elif patient_id == 'P005' and test_name == 'eGFR':
                    # Reduced for renal patient
                    value = round(45 + random.uniform(-2, 2), 0)
                else:
                    # Random normal/abnormal values
                    if random.random() < 0.8:  # 80% normal
                        value = round(random.uniform(test_info['low'], test_info['high']), 1)
                    else:  # 20% abnormal
                        value = round(test_info['high'] * random.uniform(1.1, 1.5), 1)
                
                # Determine interpretation
                if value < test_info['low']:
                    interpretation = 'Low'
                elif value > test_info['high']:
                    interpretation = 'High'
                else:
                    interpretation = 'Normal'
                
                conn.execute('''
                INSERT INTO lab_results 
                (patient_id, result_date, test_name, value, unit, reference_low, reference_high, interpretation, lab_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    patient_id, date, test_name, value, test_info['unit'],
                    test_info['low'], test_info['high'], interpretation, 'Main Hospital Lab'
                ))
    
    # ============================================
    # INSERT VITAL SIGNS (BP, HR, etc.)
    # ============================================
    
    for patient_id in ['P001', 'P002', 'P003', 'P004', 'P005']:
        for month in range(6):  # 6 months of vital signs
            date = (datetime(2023, 7, 1) + timedelta(days=30*month)).strftime('%Y-%m-%d')
            
            # Patient-specific patterns
            if patient_id == 'P001':  # Diabetic - improving BP
                systolic = 140 - (month * 3) + random.randint(-5, 5)
                diastolic = 90 - (month * 1) + random.randint(-3, 3)
            elif patient_id == 'P002':  # Hypertensive - controlled
                systolic = 125 + random.randint(-5, 5)
                diastolic = 80 + random.randint(-3, 3)
            elif patient_id == 'P003':  # Cardiac - stable
                systolic = 130 + random.randint(-5, 5)
                diastolic = 85 + random.randint(-3, 3)
            else:
                systolic = random.randint(110, 130)
                diastolic = random.randint(70, 85)
            
            conn.execute('''
            INSERT INTO vital_signs 
            (patient_id, measurement_date, systolic_bp, diastolic_bp, heart_rate, 
             temperature, respiratory_rate, oxygen_saturation, weight_kg, height_cm, bmi)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                patient_id, date, systolic, diastolic,
                random.randint(65, 85),  # Heart rate
                round(random.uniform(36.5, 37.2), 1),  # Temperature
                random.randint(12, 18),  # Respiratory rate
                random.randint(95, 99),  # Oxygen saturation
                round(random.uniform(70, 90), 1),  # Weight
                175 if patient_id in ['P001', 'P003', 'P005'] else 165,  # Height
                round(random.uniform(24, 30), 1)  # BMI
            ))
    
    # ============================================
    # INSERT MEDICATIONS
    # ============================================
    
    medications = [
        # Patient 1 - Diabetes + Hypertension
        ('P001', 'Metformin', 'Metformin', '1000 mg', 'Twice daily', 'Oral', 
         '2023-01-01', None, 'Active', 'Dr. Sarah Chen', 'CVS Pharmacy'),
        ('P001', 'Empagliflozin', 'Empagliflozin', '10 mg', 'Daily', 'Oral',
         '2023-03-15', None, 'Active', 'Dr. Sarah Chen', 'CVS Pharmacy'),
        ('P001', 'Lisinopril', 'Lisinopril', '20 mg', 'Daily', 'Oral',
         '2022-08-10', None, 'Active', 'Dr. Sarah Chen', 'CVS Pharmacy'),
        ('P001', 'Atorvastatin', 'Atorvastatin', '40 mg', 'Daily', 'Oral',
         '2022-05-20', None, 'Active', 'Dr. Sarah Chen', 'CVS Pharmacy'),
        
        # Patient 2 - Hypertension
        ('P002', 'Amlodipine', 'Amlodipine besylate', '5 mg', 'Daily', 'Oral',
         '2023-02-01', None, 'Active', 'Dr. Amanda Lee', 'Rite Aid'),
        ('P002', 'Hydrochlorothiazide', 'Hydrochlorothiazide', '25 mg', 'Daily', 'Oral',
         '2023-05-10', None, 'Active', 'Dr. Amanda Lee', 'Rite Aid'),
        ('P002', 'Omeprazole', 'Omeprazole', '20 mg', 'Daily', 'Oral',
         '2022-11-15', None, 'Active', 'Dr. Amanda Lee', 'Rite Aid'),
        
        # Patient 3 - Cardiac
        ('P003', 'Aspirin', 'Acetylsalicylic acid', '81 mg', 'Daily', 'Oral',
         '2022-01-15', None, 'Active', 'Dr. Michael Rodriguez', 'Walgreens'),
        ('P003', 'Atorvastatin', 'Atorvastatin', '80 mg', 'Daily', 'Oral',
         '2022-02-01', None, 'Active', 'Dr. Michael Rodriguez', 'Walgreens'),
        ('P003', 'Metoprolol', 'Metoprolol tartrate', '50 mg', 'Twice daily', 'Oral',
         '2022-03-10', None, 'Active', 'Dr. Michael Rodriguez', 'Walgreens'),
        
        # Patient 4 - Asthma
        ('P004', 'Albuterol', 'Albuterol sulfate', '90 mcg', 'As needed', 'Inhalation',
         '2023-01-10', None, 'Active', 'Dr. James Wilson', 'CVS Pharmacy'),
        ('P004', 'Fluticasone', 'Fluticasone propionate', '250 mcg', 'Twice daily', 'Inhalation',
         '2023-02-15', None, 'Active', 'Dr. James Wilson', 'CVS Pharmacy'),
        
        # Patient 5 - Renal
        ('P005', 'Losartan', 'Losartan potassium', '50 mg', 'Daily', 'Oral',
         '2023-03-01', None, 'Active', 'Dr. Sarah Chen', 'Walgreens'),
        ('P005', 'Furosemide', 'Furosemide', '40 mg', 'Daily', 'Oral',
         '2023-04-10', None, 'Active', 'Dr. Sarah Chen', 'Walgreens'),
    ]
    
    for med in medications:
        conn.execute('''
        INSERT INTO medications 
        (patient_id, medication_name, generic_name, dosage, frequency, route, 
         start_date, end_date, status, prescribing_physician, pharmacy)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', med)
    
    # ============================================
    # INSERT CLINICAL NOTES
    # ============================================
    
    clinical_notes = [
        # Patient 1 - Diabetes follow-up
        ('P001', '2024-01-15', 'Progress Note', 'Diabetes Follow-up',
         '''SUBJECTIVE:
Patient presents for routine diabetes follow-up. Reports good adherence to medication regimen. Mild peripheral neuropathy symptoms in feet. No episodes of hypoglycemia.

OBJECTIVE:
Vitals: BP 132/82, HR 78, Temp 98.6°F, Weight 85 kg.
Recent Labs: HbA1c 6.2% (improved), Creatinine 1.0 mg/dL, LDL 95 mg/dL.

ASSESSMENT:
1. Type 2 Diabetes Mellitus - Improved control
2. Diabetic Peripheral Neuropathy - Stable
3. Hypertension - Well-controlled

PLAN:
1. Continue current medications
2. Follow up in 3 months
3. Podiatry referral''',
         'Dr. Sarah Chen'),
        
        # Patient 2 - Hypertension check
        ('P002', '2024-01-10', 'Follow-up', 'Hypertension Management',
         '''Patient reports good adherence to medications. Denies chest pain, shortness of breath, or edema. Home BP logs show readings averaging 125/78 mmHg. Physical exam unremarkable. Recent labs within normal limits.

Plan: Continue current therapy, follow up in 2 months.''',
         'Dr. Amanda Lee'),
        
        # Patient 3 - Cardiology visit
        ('P003', '2024-01-20', 'Consultation', 'Cardiac Evaluation',
         '''Patient with known CAD presents for routine follow-up. Reports stable exercise tolerance. Denies chest pain or palpitations. ECG shows normal sinus rhythm. LDL cholesterol at goal.

Continue current cardiac medications. Schedule stress test in 6 months.''',
         'Dr. Michael Rodriguez'),
    ]
    
    for note in clinical_notes:
        conn.execute('''
        INSERT INTO clinical_notes 
        (patient_id, note_date, note_type, title, content, physician)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', note)
    
    conn.commit()
    conn.close()
    
    print("✅ Complete database created with ALL medical records!")
    return True

# ============================================
# 2. INTELLIGENT QUERY PROCESSOR
# ============================================
class CompleteClinicalAssistant:
    def __init__(self, db_path='complete_clinical.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
    
    def get_patient_list(self):
        """Get list of all patients"""
        query = '''
        SELECT patient_id, first_name || ' ' || last_name as name, 
               age, gender, primary_diagnosis
        FROM patients 
        ORDER BY last_name
        '''
        df = pd.read_sql_query(query, self.conn)
        return df.to_dict('records')
    
    def get_patient_info(self, patient_id):
        """Get basic patient information"""
        query = "SELECT * FROM patients WHERE patient_id = ?"
        df = pd.read_sql_query(query, self.conn, params=[patient_id])
        return df.to_dict('records')[0] if not df.empty else None
    
    def get_blood_pressure_data(self, patient_id):
        """Get blood pressure data"""
        query = '''
        SELECT measurement_date, systolic_bp, diastolic_bp, heart_rate
        FROM vital_signs 
        WHERE patient_id = ?
        ORDER BY measurement_date
        '''
        df = pd.read_sql_query(query, self.conn, params=[patient_id])
        return df
    
    def get_hba1c_data(self, patient_id):
        """Get HbA1c trend data"""
        query = '''
        SELECT result_date, value, unit, interpretation
        FROM lab_results 
        WHERE patient_id = ? AND test_name = 'HbA1c'
        ORDER BY result_date
        '''
        df = pd.read_sql_query(query, self.conn, params=[patient_id])
        return df
    
    def get_medications(self, patient_id):
        """Get medications"""
        query = '''
        SELECT medication_name, dosage, frequency, start_date, status
        FROM medications 
        WHERE patient_id = ?
        ORDER BY status DESC, start_date DESC
        '''
        df = pd.read_sql_query(query, self.conn, params=[patient_id])
        return df
    
    def get_recent_labs(self, patient_id, limit=10):
        """Get recent lab results"""
        query = f'''
        SELECT test_name, result_date, value, unit, interpretation
        FROM lab_results 
        WHERE patient_id = ?
        ORDER BY result_date DESC
        LIMIT {limit}
        '''
        df = pd.read_sql_query(query, self.conn, params=[patient_id])
        return df
    
    def get_clinical_summary(self, patient_id):
        """Generate comprehensive clinical summary"""
        patient = self.get_patient_info(patient_id)
        if not patient:
            return "Patient not found."
        
        # Gather all data
        bp_data = self.get_blood_pressure_data(patient_id)
        hba1c_data = self.get_hba1c_data(patient_id)
        medications = self.get_medications(patient_id)
        recent_labs = self.get_recent_labs(patient_id, 5)
        
        # Build summary
        summary = f"""# 📋 COMPREHENSIVE CLINICAL SUMMARY
**Patient:** {patient['first_name']} {patient['last_name']}
**Age/Gender:** {patient['age']} {patient['gender']}
**Primary Diagnosis:** {patient['primary_diagnosis']}
**Secondary:** {patient['secondary_diagnosis']}
**Allergies:** {patient['allergies']}
**Last Visit:** {patient['last_visit']}
**Next Appointment:** {patient['next_appointment']}

## 🔍 Key Clinical Data"""
        
        # Blood Pressure
        if not bp_data.empty:
            latest_bp = bp_data.iloc[-1]
            summary += f"\n**Blood Pressure:** {latest_bp['systolic_bp']}/{latest_bp['diastolic_bp']} mmHg"
            if len(bp_data) > 1:
                first_bp = bp_data.iloc[0]
                change = latest_bp['systolic_bp'] - first_bp['systolic_bp']
                summary += f" ({'Improved' if change < 0 else 'Worsened'} by {abs(change)} mmHg over {len(bp_data)} readings)"
        
        # HbA1c
        if not hba1c_data.empty:
            latest_hba1c = hba1c_data.iloc[-1]
            summary += f"\n**HbA1c:** {latest_hba1c['value']}% ({latest_hba1c['interpretation']})"
            if latest_hba1c['value'] < 7.0:
                summary += " ✅ Well-controlled"
            else:
                summary += " ⚠️ Needs improvement"
        
        # Medications
        active_meds = medications[medications['status'] == 'Active']
        if not active_meds.empty:
            summary += f"\n**Active Medications:** {len(active_meds)} prescriptions"
        
        # Recent Labs
        abnormal_labs = recent_labs[recent_labs['interpretation'] != 'Normal']
        if not abnormal_labs.empty:
            summary += f"\n**Alerts:** {len(abnormal_labs)} abnormal lab results"
            for _, lab in abnormal_labs.iterrows():
                summary += f"\n  - {lab['test_name']}: {lab['value']} {lab['unit']} ({lab['interpretation']})"
        
        # Clinical Assessment
        summary += "\n\n## 🩺 Clinical Assessment"
        
        assessments = []
        
        # Diabetes assessment
        if not hba1c_data.empty:
            latest = hba1c_data.iloc[-1]
            if latest['value'] < 7.0:
                assessments.append("Diabetes well-controlled per ADA guidelines")
            else:
                assessments.append("Diabetes control needs optimization")
        
        # Hypertension assessment
        if not bp_data.empty:
            latest = bp_data.iloc[-1]
            if latest['systolic_bp'] < 130 and latest['diastolic_bp'] < 80:
                assessments.append("Blood pressure at goal")
            else:
                assessments.append("Blood pressure above target")
        
        # Medication assessment
        if len(active_meds) > 5:
            assessments.append("Polypharmacy - consider medication review")
        
        if assessments:
            for assess in assessments:
                summary += f"\n- {assess}"
        else:
            summary += "\n- Overall stable condition"
        
        # Recommendations
        summary += "\n\n## 📋 Recommendations"
        summary += "\n1. Continue current management plan"
        summary += "\n2. Monitor key parameters regularly"
        summary += "\n3. Follow up as scheduled"
        summary += "\n4. Address any abnormal lab results"
        
        return summary
    
    def process_query(self, patient_id, query):
        """Process natural language query"""
        query_lower = query.lower()
        
        response = {
            'answer': '',
            'data': None,
            'visualization': None,
            'type': 'text'
        }
        
        patient = self.get_patient_info(patient_id)
        if not patient:
            response['answer'] = "Patient not found."
            return response
        
        patient_name = f"{patient['first_name']} {patient['last_name']}"
        
        # Blood pressure queries
        if any(word in query_lower for word in ['blood pressure', 'bp', 'pressure', 'hypertension']):
            bp_data = self.get_blood_pressure_data(patient_id)
            
            if bp_data.empty:
                response['answer'] = f"No blood pressure records for {patient_name}."
                return response
            
            latest = bp_data.iloc[-1]
            
            if 'trend' in query_lower or 'over time' in query_lower or 'history' in query_lower:
                # Show trend
                response['answer'] = f"""**Blood Pressure Trend for {patient_name}:**
                
Latest: {latest['systolic_bp']}/{latest['diastolic_bp']} mmHg
{len(bp_data)} readings over {len(bp_data['measurement_date'].unique())} months"""
                
                # Create visualization
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=bp_data['measurement_date'], y=bp_data['systolic_bp'],
                    mode='lines+markers',
                    name='Systolic',
                    line=dict(color='red', width=2)
                ))
                fig.add_trace(go.Scatter(
                    x=bp_data['measurement_date'], y=bp_data['diastolic_bp'],
                    mode='lines+markers',
                    name='Diastolic',
                    line=dict(color='blue', width=2)
                ))
                fig.add_hrect(y0=0, y1=120, line_width=0, fillcolor="green", opacity=0.1)
                fig.add_hrect(y0=120, y1=130, line_width=0, fillcolor="yellow", opacity=0.1)
                fig.add_hrect(y0=130, y1=180, line_width=0, fillcolor="red", opacity=0.1)
                
                fig.update_layout(
                    title='Blood Pressure Trend',
                    xaxis_title='Date',
                    yaxis_title='BP (mmHg)',
                    hovermode='x unified'
                )
                response['visualization'] = fig
                response['data'] = bp_data
                
            else:
                # Show latest
                response['answer'] = f"""**Blood Pressure for {patient_name}:**
                
**Latest Reading:** {latest['systolic_bp']}/{latest['diastolic_bp']} mmHg
**Date:** {latest['measurement_date']}
**Heart Rate:** {latest['heart_rate']} bpm"""
                
                # Interpretation
                if latest['systolic_bp'] < 120 and latest['diastolic_bp'] < 80:
                    response['answer'] += "\n\n✅ **Normal** blood pressure"
                elif latest['systolic_bp'] < 130 and latest['diastolic_bp'] < 80:
                    response['answer'] += "\n\n⚠️ **Elevated** blood pressure"
                elif latest['systolic_bp'] < 140 or latest['diastolic_bp'] < 90:
                    response['answer'] += "\n\n🟡 **Stage 1 Hypertension**"
                else:
                    response['answer'] += "\n\n🔴 **Stage 2 Hypertension**"
                
                response['data'] = bp_data.tail(5)
        
        # HbA1c queries
        elif any(word in query_lower for word in ['hba1c', 'a1c', 'diabetes', 'sugar']):
            hba1c_data = self.get_hba1c_data(patient_id)
            
            if hba1c_data.empty:
                response['answer'] = f"No HbA1c records for {patient_name}."
                return response
            
            latest = hba1c_data.iloc[-1]
            
            if 'trend' in query_lower or 'over time' in query_lower:
                # Show trend
                response['answer'] = f"""**HbA1c Trend for {patient_name}:**
                
Latest: {latest['value']}% ({latest['result_date']})
{len(hba1c_data)} readings over {len(hba1c_data['result_date'].unique())} months"""
                
                # Create visualization
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=hba1c_data['result_date'], y=hba1c_data['value'],
                    mode='lines+markers',
                    name='HbA1c',
                    line=dict(color='red', width=3)
                ))
                fig.add_hline(y=5.7, line_dash="dash", line_color="green", 
                             annotation_text="Normal", annotation_position="bottom right")
                fig.add_hline(y=6.5, line_dash="dash", line_color="orange",
                             annotation_text="Diabetes Threshold")
                fig.add_hline(y=7.0, line_dash="dash", line_color="red",
                             annotation_text="Control Target")
                
                fig.update_layout(
                    title='HbA1c Trend Over Time',
                    xaxis_title='Date',
                    yaxis_title='HbA1c (%)'
                )
                response['visualization'] = fig
                response['data'] = hba1c_data
                
            else:
                # Show latest
                response['answer'] = f"""**HbA1c for {patient_name}:**
                
**Value:** {latest['value']}%
**Date:** {latest['result_date']}
**Interpretation:** {latest['interpretation']}"""
                
                # Clinical context
                if latest['value'] < 5.7:
                    response['answer'] += "\n\n✅ **Normal** (non-diabetic range)"
                elif latest['value'] < 6.5:
                    response['answer'] += "\n\n⚠️ **Pre-diabetes**"
                elif latest['value'] < 7.0:
                    response['answer'] += "\n\n✅ **Diabetes, well-controlled**"
                else:
                    response['answer'] += "\n\n🔴 **Diabetes, needs improvement**"
                
                response['data'] = hba1c_data.tail(3)
        
        # Medication queries
        elif any(word in query_lower for word in ['medication', 'medications', 'drug', 'prescription', 'meds']):
            medications = self.get_medications(patient_id)
            
            if medications.empty:
                response['answer'] = f"No medication records for {patient_name}."
                return response
            
            active_meds = medications[medications['status'] == 'Active']
            
            response['answer'] = f"""**Medications for {patient_name}:**
            
**Active Medications ({len(active_meds)}):**"""
            
            for idx, med in active_meds.iterrows():
                response['answer'] += f"\n{idx+1}. **{med['medication_name']}** - {med['dosage']} {med['frequency']} (since {med['start_date']})"
            
            if len(active_meds) > 5:
                response['answer'] += "\n\n⚠️ **Note:** Patient is on multiple medications. Consider medication review."
            
            response['data'] = medications
        
        # Lab results queries
        elif any(word in query_lower for word in ['lab', 'test', 'result', 'labs']):
            recent_labs = self.get_recent_labs(patient_id, 10)
            
            if recent_labs.empty:
                response['answer'] = f"No lab results for {patient_name}."
                return response
            
            latest_date = recent_labs['result_date'].iloc[0]
            today_labs = recent_labs[recent_labs['result_date'] == latest_date]
            
            response['answer'] = f"""**Recent Lab Results for {patient_name}:**
            
**Most Recent Tests ({latest_date}):**"""
            
            for _, lab in today_labs.iterrows():
                icon = "✅" if lab['interpretation'] == 'Normal' else "⚠️"
                response['answer'] += f"\n{icon} **{lab['test_name']}:** {lab['value']} {lab['unit']} ({lab['interpretation']})"
            
            # Abnormal labs
            abnormal_labs = recent_labs[recent_labs['interpretation'] != 'Normal']
            if not abnormal_labs.empty:
                response['answer'] += f"\n\n**Alerts:** {len(abnormal_labs)} abnormal results"
            
            response['data'] = recent_labs
        
        # Summary queries
        elif any(word in query_lower for word in ['summary', 'overview', 'report', 'status']):
            summary = self.get_clinical_summary(patient_id)
            response['answer'] = summary
            response['type'] = 'summary'
        
        # General queries
        else:
            response['answer'] = f"""I can help you with {patient_name}'s clinical data. Try asking about:

• Blood pressure readings or trends
• HbA1c levels and diabetes control  
• Current medications
• Lab results and tests
• Complete clinical summary

Examples: 
- "What's the blood pressure?"
- "Show HbA1c trend over time"
- "List current medications"
- "Recent lab results"
- "Give me a patient summary" """
        
        return response

# ============================================
# 3. STREAMLIT INTERFACE
# ============================================
def main():
    # Page configuration
    st.set_page_config(
        page_title="Doctor's Clinical Assistant",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .patient-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-left: 4px solid #007bff;
        padding: 15px;
        border-radius: 8px;
        margin: 5px 0;
    }
    .alert-card {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 15px;
        border-radius: 8px;
        margin: 5px 0;
    }
    .chat-user {
        background-color: #e3f2fd;
        padding: 10px 15px;
        border-radius: 10px;
        margin: 5px 0;
        border-left: 4px solid #2196f3;
    }
    .chat-assistant {
        background-color: #f3e5f5;
        padding: 10px 15px;
        border-radius: 10px;
        margin: 5px 0;
        border-left: 4px solid #9c27b0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize database
    if 'db_created' not in st.session_state:
        with st.spinner("🔄 Creating comprehensive clinical database..."):
            create_complete_database()
        st.session_state.db_created = True
    
    # Initialize assistant
    if 'assistant' not in st.session_state:
        st.session_state.assistant = CompleteClinicalAssistant()
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Initialize selected patient
    if 'selected_patient' not in st.session_state:
        st.session_state.selected_patient = 'P001'
    
    # ============================================
    # SIDEBAR
    # ============================================
    with st.sidebar:
        st.title("🏥 Clinical Assistant")
        st.markdown("---")
        
        # Patient selection
        st.subheader("👥 Select Patient")
        
        patients = st.session_state.assistant.get_patient_list()
        
        for patient in patients:
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button(
                    f"{patient['name']}",
                    key=f"pat_{patient['patient_id']}",
                    use_container_width=True
                ):
                    st.session_state.selected_patient = patient['patient_id']
                    # Add system message
                    st.session_state.chat_history.append({
                        "role": "system",
                        "content": f"Selected patient: {patient['name']}"
                    })
                    st.rerun()
            with col2:
                st.caption(f"{patient['age']}{patient['gender'][0]}")
        
        st.markdown("---")
        
        # Quick actions
        st.subheader("🚀 Quick Actions")
        
        quick_actions = [
            ("📊 BP Trend", "Show blood pressure trend"),
            ("🩸 HbA1c", "Show HbA1c results"),
            ("💊 Meds", "List medications"),
            ("🔬 Labs", "Recent lab results"),
            ("📋 Summary", "Patient summary")
        ]
        
        for emoji, query in quick_actions:
            if st.button(f"{emoji} {query.split()[0]}", 
                        key=f"quick_{query}",
                        use_container_width=True):
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": query
                })
                st.rerun()
        
        st.markdown("---")
        
        # System controls
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
        
        if st.button("🔄 Refresh Data", use_container_width=True):
            create_complete_database()
            st.success("Database refreshed!")
            st.rerun()
        
        # Stats
        st.markdown("---")
        st.subheader("📊 Statistics")
        st.metric("Total Patients", len(patients))
        st.metric("Chat Messages", len(st.session_state.chat_history))
    
    # ============================================
    # MAIN INTERFACE
    # ============================================
    
    # Header
    st.title("💬 Doctor's Clinical Assistant")
    st.markdown("**Access complete patient records with natural language queries**")
    
    # Get patient info
    patient_info = st.session_state.assistant.get_patient_info(st.session_state.selected_patient)
    
    if not patient_info:
        st.error("Patient not found")
        return
    
    patient_name = f"{patient_info['first_name']} {patient_info['last_name']}"
    
    # Patient header
    st.markdown(f"""
    <div class="patient-header">
    <h2>👤 {patient_name}</h2>
    <p><strong>Age:</strong> {patient_info['age']} | <strong>Gender:</strong> {patient_info['gender']} | 
    <strong>Diagnosis:</strong> {patient_info['primary_diagnosis']}</p>
    <p><strong>Last Visit:</strong> {patient_info['last_visit']} | 
    <strong>Next Appointment:</strong> {patient_info['next_appointment']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Blood pressure
        bp_data = st.session_state.assistant.get_blood_pressure_data(st.session_state.selected_patient)
        if not bp_data.empty:
            latest_bp = bp_data.iloc[-1]
            st.metric("Blood Pressure", f"{latest_bp['systolic_bp']}/{latest_bp['diastolic_bp']}")
        else:
            st.metric("Blood Pressure", "No data")
    
    with col2:
        # HbA1c
        hba1c_data = st.session_state.assistant.get_hba1c_data(st.session_state.selected_patient)
        if not hba1c_data.empty:
            latest_hba1c = hba1c_data.iloc[-1]
            st.metric("HbA1c", f"{latest_hba1c['value']}%")
        else:
            st.metric("HbA1c", "No data")
    
    with col3:
        # Medications
        medications = st.session_state.assistant.get_medications(st.session_state.selected_patient)
        active_meds = medications[medications['status'] == 'Active']
        st.metric("Active Meds", len(active_meds))
    
    with col4:
        # Recent labs
        recent_labs = st.session_state.assistant.get_recent_labs(st.session_state.selected_patient, 5)
        abnormal = recent_labs[recent_labs['interpretation'] != 'Normal']
        st.metric("Abnormal Labs", len(abnormal))
    
    st.markdown("---")
    
    # ============================================
    # CHAT INTERFACE
    # ============================================
    st.subheader("💬 Clinical Query Assistant")
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-user">
                <strong>👨‍⚕️ Physician:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            
            elif message["role"] == "assistant":
                st.markdown(f"""
                <div class="chat-assistant">
                <strong>🤖 Assistant:</strong>
                """, unsafe_allow_html=True)
                
                # Display the response content
                lines = message["content"].split('\n')
                for line in lines:
                    if line.strip():
                        if line.startswith('# '):
                            st.markdown(f"**{line[2:]}**")
                        elif line.startswith('## '):
                            st.markdown(f"### {line[3:]}")
                        elif line.startswith('**'):
                            st.markdown(line)
                        else:
                            st.write(line)
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Show data if available
                if "data" in message and message["data"] is not None:
                    with st.expander("📊 View Detailed Data"):
                        if isinstance(message["data"], pd.DataFrame):
                            st.dataframe(message["data"], use_container_width=True)
                
                # Show visualization if available
                if "visualization" in message and message["visualization"] is not None:
                    st.plotly_chart(message["visualization"], use_container_width=True)
            
            elif message["role"] == "system":
                st.info(f"🔔 {message['content']}")
    
    # ============================================
    # QUERY INPUT
    # ============================================
    st.markdown("---")
    st.markdown("### 🔍 Ask a Clinical Question")
    
    # Create form for query input
    with st.form("query_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            user_query = st.text_input(
                "Enter your question:",
                placeholder=f"Ask about {patient_name}'s health data...",
                key="query_input",
                label_visibility="collapsed"
            )
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("Ask", type="primary")
    
    # Process query
    if submit and user_query:
        # Add user message
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_query
        })
        
        # Get response
        with st.spinner("🔍 Analyzing clinical data..."):
            response = st.session_state.assistant.process_query(
                st.session_state.selected_patient,
                user_query
            )
        
        # Add assistant response
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response['answer'],
            "data": response.get('data'),
            "visualization": response.get('visualization')
        })
        
        st.rerun()
    
    # ============================================
    # EXAMPLE QUERIES
    # ============================================
    st.markdown("---")
    st.markdown("### 💡 Example Queries (Try These!)")
    
    examples = [
        "What's the blood pressure trend?",
        "Show HbA1c over time",
        "List current medications",
        "Show recent lab results",
        "Give me a complete patient summary",
        "How's the diabetes control?",
        "BP readings this year",
        "Medications for hypertension",
        "Latest HbA1c value",
        "Abnormal lab results"
    ]
    
    cols = st.columns(5)
    for idx, example in enumerate(examples):
        with cols[idx % 5]:
            if st.button(example, key=f"ex_{idx}", use_container_width=True):
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": example
                })
                st.rerun()
    
    # ============================================
    # DATA PREVIEW
    # ============================================
    with st.expander("📁 Preview Available Data"):
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Lab Results", "🩺 Vital Signs", "💊 Medications", "📝 Clinical Notes"])
        
        with tab1:
            labs = st.session_state.assistant.get_recent_labs(st.session_state.selected_patient, 10)
            if not labs.empty:
                st.dataframe(labs, use_container_width=True)
            else:
                st.info("No lab results available")
        
        with tab2:
            vitals = st.session_state.assistant.get_blood_pressure_data(st.session_state.selected_patient)
            if not vitals.empty:
                st.dataframe(vitals, use_container_width=True)
            else:
                st.info("No vital signs available")
        
        with tab3:
            meds = st.session_state.assistant.get_medications(st.session_state.selected_patient)
            if not meds.empty:
                st.dataframe(meds, use_container_width=True)
            else:
                st.info("No medications available")
        
        with tab4:
            # Get clinical notes
            conn = sqlite3.connect('complete_clinical.db', check_same_thread=False)
            notes_df = pd.read_sql_query(
                "SELECT note_date, title, physician FROM clinical_notes WHERE patient_id = ? ORDER BY note_date DESC",
                conn,
                params=[st.session_state.selected_patient]
            )
            conn.close()
            
            if not notes_df.empty:
                st.dataframe(notes_df, use_container_width=True)
            else:
                st.info("No clinical notes available")

if __name__ == "__main__":
    main()