import pandas as pd
from database import get_db_connection
import sqlite3
import streamlit as st
from datetime import datetime, timedelta

class ClinicalBackend:
    def __init__(self):
        self.conn = get_db_connection()

    def get_all_patients(self):
        return pd.read_sql_query("SELECT * FROM patients ORDER BY patient_id", self.conn)

    def add_patient(self, pt_data):
        """
        pt_data: dict containing patient details
        """
        try:
            with self.conn:
                self.conn.execute('''
                INSERT INTO patients (patient_id, first_name, last_name, date_of_birth, age, gender, contact_number, email, address, primary_diagnosis, allergies, last_visit)
                VALUES (:patient_id, :first_name, :last_name, :date_of_birth, :age, :gender, :contact_number, :email, :address, :primary_diagnosis, :allergies, :last_visit)
                ''', pt_data)
            return True, "Patient added successfully"
        except sqlite3.IntegrityError:
            return False, "Error: Patient ID already exists"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def add_appointment(self, appt_data):
        try:
            with self.conn:
                self.conn.execute('''
                INSERT INTO appointments (patient_id, appointment_date, appointment_time, doctor_name, reason, status, notes)
                VALUES (:patient_id, :appointment_date, :appointment_time, :doctor_name, :reason, :status, :notes)
                ''', appt_data)
            return True, "Appointment scheduled successfully"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def get_patient_details(self, patient_id):
        patient = pd.read_sql_query("SELECT * FROM patients WHERE patient_id = ?", self.conn, params=[patient_id])
        if patient.empty:
            return None
        return patient.iloc[0].to_dict()

    def get_patient_labs(self, patient_id):
        return pd.read_sql_query("SELECT * FROM lab_results WHERE patient_id = ? ORDER BY result_date DESC", self.conn, params=[patient_id])

    def get_patient_appointments(self, patient_id):
        return pd.read_sql_query("SELECT * FROM appointments WHERE patient_id = ? ORDER BY appointment_date DESC", self.conn, params=[patient_id])
    
    def get_patient_medications(self, patient_id):
        return pd.read_sql_query("SELECT * FROM medications WHERE patient_id = ? ORDER BY status ASC, start_date DESC", self.conn, params=[patient_id])

    def get_clinical_summary(self, patient_id):
        """Generate comprehensive clinical summary (Logic from original RAG system)"""
        patient = self.get_patient_details(patient_id)
        if not patient:
            return "Patient not found."
        
        # Gather all data (Retrieval Step)
        labs = self.get_patient_labs(patient_id)
        appts = self.get_patient_appointments(patient_id)
        meds = self.get_patient_medications(patient_id)
        
        # Build Context (Generation Step - Template Based)
        summary = f"""### 📋 Patient Summary: {patient['first_name']} {patient['last_name']}
**Demographics:** {patient['age']}y {patient['gender']}
**Diagnosis:** {patient['primary_diagnosis']}
**Last Visit:** {patient['last_visit']}

#### 🔍 Recent Clinical Data
"""
        
        if not meds.empty:
            summary += f"\n**Current Medications:**"
            active_meds = meds[meds['status'] == 'Active']
            if not active_meds.empty:
                for _, med in active_meds.iterrows():
                    summary += f"\n- {med['medication_name']} {med['dosage']} ({med['frequency']})"
            else:
                summary += "\n*No active medications.*"
        else:
            summary += "\n*No medication history.*"
        
        if not labs.empty:
            summary += f"\n\n**Recent Lab Results ({len(labs)}):**"
            # Sort by date and show more results (up to 15) to cover expanded panels
            labs_sorted = labs.sort_values('result_date', ascending=False)
            for _, lab in labs_sorted.head(15).iterrows():
                icon = "✅" if lab['interpretation'] == 'Normal' else "⚠️"
                summary += f"\n- {icon} {lab['test_name']}: {lab['value']} {lab['unit']} ({lab['interpretation']}) on {lab['result_date']}"
        else:
            summary += "\n\n*No lab results found.*"

        if not appts.empty:
            summary += f"\n\n**Recent Appointments ({len(appts)}):**"
            for _, appt in appts.head(3).iterrows():
                summary += f"\n- {appt['appointment_date']}: {appt['reason']} ({appt['status']})"
        else:
            summary += "\n\n*No appointments found.*"
            
        return summary

    def get_styles(self):
        """Returns shared CSS from app.css for a premium, modern clinical look."""
        try:
            with open("app.css", "r") as f:
                css = f.read()
            return f"<style>{css}</style>"
        except FileNotFoundError:
            return ""

    def run_analysis_query(self, query, patient_id=None):
        # Intelligent Query Router (Simulated RAG)
        response = ""
        query = query.lower()
        
        if patient_id:
            pt = self.get_patient_details(patient_id)
            if not pt: return "Patient not found"
            
            # Helper for date filtering
            def filter_by_time(df, date_col, query_text):
                import re
                try:
                    # Fix reference time to simulated current date (End of 2025)
                    now = pd.to_datetime("2025-12-31")
                    cutoff = None
                    
                    # Regex for "last X years"
                    year_match = re.search(r'last (\d+) years?', query_text)
                    if year_match:
                        years = int(year_match.group(1))
                        cutoff = now - pd.DateOffset(years=years)
                    elif 'last year' in query_text:
                        cutoff = now - pd.DateOffset(years=1)
                    
                    # Regex for "last X months"
                    month_match = re.search(r'last (\d+) months?', query_text)
                    if month_match:
                        months = int(month_match.group(1))
                        cutoff = now - pd.DateOffset(months=months)
                        
                    if cutoff is None:
                        return df # No filter found
                    
                    df[date_col] = pd.to_datetime(df[date_col])
                    return df[df[date_col] > cutoff]
                except Exception:
                    return df
                    

            
            # Intent Recognition
            # Specific Component Intents
            if any(x in query.lower() for x in ['medication', 'medicine', 'drug', 'prescription', 'taking']):
                meds = self.get_patient_medications(patient_id)
                if meds.empty:
                    response = f"No medication history found for {pt['first_name']}."
                else:
                    active = meds[meds['status'] == 'Active']
                    discontinued = meds[meds['status'] == 'Discontinued']
                    
                    # Detect intent for specific status
                    show_active = any(x in query for x in ['active', 'current', 'taking', 'now'])
                    show_discontinued = any(x in query for x in ['discontinued', 'past', 'history', 'stopped', 'old'])
                    
                    # If neither specified, show both (default)
                    if not show_active and not show_discontinued:
                        show_active = True
                        show_discontinued = True
                    
                    response = f"**Medications for {pt['first_name']}**"
                    if show_active and not show_discontinued: response += " (Active only)"
                    if show_discontinued and not show_active: response += " (Discontinued only)"
                    response += ":\n"
                    
                    if show_active:
                        if not active.empty:
                            response += "\n*Active:*\n"
                            for _, med in active.iterrows():
                                response += f"- **{med['medication_name']}** {med['dosage']} ({med['frequency']})\n"
                        else:
                            response += "\n*Active:* None\n"
                            
                    if show_discontinued:
                        if not discontinued.empty:
                            response += "\n*Discontinued:*\n"
                            for _, med in discontinued.iterrows():
                                response += f"- {med['medication_name']} (Ended {med['end_date']})\n"
                        else:
                            response += "\n*Discontinued:* None\n"
                            
            elif any(x in query.lower() for x in ['lab', 'result', 'test', 'blood', 'glucose', 'a1c', 'bp', 'pressure', 'cholesterol', 'hemoglobin', 'bun', 'ldl', 'hdl', 'triglycerides', 'creatinine', 'lipid']):
                labs = self.get_patient_labs(patient_id)
                labs['result_date'] = pd.to_datetime(labs['result_date'])
                
                # Apply time filter if requested (past 1 year, 2 years, etc)
                labs = filter_by_time(labs, 'result_date', query)
                
                # Identify which specific tests are being asked for
                all_test_names = labs['test_name'].unique()
                requested_tests = []
                
                # Check for aliases and test names in query
                if any(x in query for x in ['bp', 'blood pressure', 'pressure']):
                    requested_tests.extend([t for t in all_test_names if 'BP' in t])
                
                if 'lipid' in query:
                    # Lipid panel usually includes everything
                    requested_tests.extend([t for t in all_test_names if any(l in t for l in ['Cholesterol', 'LDL', 'HDL', 'Triglycerides'])])
                elif 'cholesterol' in query:
                    # Cholesterol specifically (excluding triglycerides by user request)
                    requested_tests.extend([t for t in all_test_names if 'Cholesterol' in t or any(l in t for l in ['LDL', 'HDL'])])
                
                if 'triglyceride' in query:
                    requested_tests.extend([t for t in all_test_names if 'Triglycerides' in t])
                
                # Specific components
                for comp in ['LDL', 'HDL', 'A1c', 'Glucose', 'Hemoglobin', 'BUN', 'Creatinine']:
                    if comp.lower() in query:
                        requested_tests.extend([t for t in all_test_names if comp in t])
                
                # Direct match for any other unique tests that might be in the query
                for t in all_test_names:
                    if t.lower() in query and t not in requested_tests:
                        requested_tests.append(t)
                
                # Deduplicate
                requested_tests = list(set(requested_tests))
                
                # Filter records
                if requested_tests:
                    filtered_labs = labs[labs['test_name'].isin(requested_tests)]
                else:
                    # If it's a general "show labs" query, just use everything (will be limited in display)
                    filtered_labs = labs
                
                if not filtered_labs.empty:
                    # Sort Descending (Newest First)
                    filtered_labs = filtered_labs.sort_values(by='result_date', ascending=False)
                    
                    response = f"**Laboratory Analysis for {pt['first_name']}:**\n\n"
                    
                    if requested_tests:
                         response += "| Date | Test | Value | Status |\n"
                         response += "|---|---|---|---|\n"
                         # Show up to 20 matching records for specific tests
                         for _, row in filtered_labs.head(20).iterrows():
                             date_str = row['result_date'].strftime('%Y-%m-%d')
                             response += f"| {date_str} | {row['test_name']} | {row['value']} {row['unit']} | {row['interpretation']} |\n"
                    else:
                         # For general "show labs" queries, provide a bulleted list of the top 10
                         for _, row in filtered_labs.head(10).iterrows():
                             date_str = row['result_date'].strftime('%Y-%m-%d')
                             response += f"- **{date_str}**: {row['test_name']} = {row['value']} {row['unit']} ({row['interpretation']})\n"
                else:
                    response = "No matching lab results found for the specified tests or time period."
                        
            elif any(x in query.lower() for x in ['appointment', 'visit', 'scheduled', 'checkup']):
                appts = self.get_patient_appointments(patient_id)
                # appts = filter_by_time(appts, 'appointment_date', query) # OLD Logic
                
                # Enhanced Logic for specific dates (Today, Tomorrow, Yesterday)
                target_date_str = None
                date_label = ""
                
                today_obj = datetime.now()
                
                if 'today' in query:
                    target_date_str = today_obj.strftime('%Y-%m-%d')
                    date_label = f"today ({target_date_str})"
                elif 'tomorrow' in query:
                    target_date_str = (today_obj + timedelta(days=1)).strftime('%Y-%m-%d')
                    date_label = f"tomorrow ({target_date_str})"
                elif 'yesterday' in query:
                    target_date_str = (today_obj - timedelta(days=1)).strftime('%Y-%m-%d')
                    date_label = f"yesterday ({target_date_str})"
                
                if target_date_str:
                    # Filter for the specific date
                    specific_appts = appts[appts['appointment_date'] == target_date_str]
                    
                    if not specific_appts.empty:
                        response = f"**Yes, there is an appointment {date_label}:**\n"
                        for _, appt in specific_appts.iterrows():
                            response += f"- **{appt['appointment_time']}**: {appt['reason']} with **{appt['doctor_name']}** ({appt['status']})\n"
                    else:
                        response = f"No appointments found for {date_label}."
                        
                else:
                    # General History / Future Logic
                    if 'upcoming' in query or 'next' in query:
                        # Simple string comparison works for ISO dates
                        today_str = today_obj.strftime('%Y-%m-%d')
                        upcoming = appts[appts['appointment_date'] >= today_str]
                        if not upcoming.empty:
                             response = f"**Upcoming Appointments:**\n"
                             for _, appt in upcoming.sort_values('appointment_date').iterrows():
                                response += f"- {appt['appointment_date']} @ {appt['appointment_time']}: {appt['reason']} ({appt['doctor_name']})\n"
                        else:
                            response = "No upcoming appointments found."
                    else:
                        # Default history
                        response = f"**Appointment History for {pt['first_name']}:**\n"
                        for _, appt in appts.head(10).iterrows():
                            # Sort by date desc for history
                            response += f"- {appt['appointment_date']}: {appt['reason']} with {appt['doctor_name']}\n"
            
            # General Summary Intent (Lower Priority - used if no specific component found)
            elif any(x in query for x in ['summary', 'overview', 'report', 'status']):
                response = self.get_clinical_summary(patient_id)
            
            else:
                response = f"I can help you analyze {pt['first_name']}'s data. Try asking for a 'summary', 'medications', 'lab results', or 'appointments'."
                
        else:
            response = "Please select a patient first to analyze their records."
                
        return response
