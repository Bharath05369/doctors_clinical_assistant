import streamlit as st
import pandas as pd
from datetime import date
from backend import ClinicalBackend

st.set_page_config(page_title="Add Records", page_icon="➕", layout="wide")

def main():
    backend = ClinicalBackend()
    st.markdown('<h1 class="main-header">Clinical Records Management</h1>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Add New Patient", "Schedule Appointment"])
    
    # --- Add Patient Tab ---
    with tab1:
        st.subheader("Register New Patient")
        with st.form("new_patient_form"):
            col1, col2 = st.columns(2)
            with col1:
                p_id = st.text_input("Patient ID (Unique, e.g., P999)")
                fname = st.text_input("First Name")
                lname = st.text_input("Last Name")
                gender = st.selectbox("Gender", ["M", "F", "Other"])
                dob = st.date_input("Date of Birth", min_value=date(1900, 1, 1))
            
            with col2:
                contact = st.text_input("Contact Number")
                email = st.text_input("Email")
                address = st.text_area("Address")
                diagnosis = st.text_input("Primary Diagnosis")
                allergies = st.text_input("Allergies (comma separated)")
                
            submitted = st.form_submit_button("Register Patient")
            
            if submitted:
                if p_id and fname and lname:
                    age = date.today().year - dob.year
                    pt_data = {
                        'patient_id': p_id,
                        'first_name': fname,
                        'last_name': lname,
                        'date_of_birth': str(dob),
                        'age': age,
                        'gender': gender,
                        'contact_number': contact,
                        'email': email,
                        'address': address,
                        'primary_diagnosis': diagnosis,
                        'allergies': allergies,
                        'last_visit': str(date.today())
                    }
                    success, msg = backend.add_patient(pt_data)
                    if success:
                        st.success(f"Success: {msg}")
                    else:
                        st.error(f"Error: {msg}")
                else:
                    st.warning("Please fill in required fields (ID, Name)")

    # --- Add Appointment Tab ---
    with tab2:
        st.subheader("Schedule Appointment")
        
        # Select existing patient
        all_patients = backend.get_all_patients()
        if all_patients.empty:
            st.error("No patients in database. Please add a patient first.")
        else:
            patient_list = all_patients.apply(lambda x: f"{x['patient_id']} - {x['first_name']} {x['last_name']}", axis=1)
            selected_pt = st.selectbox("Select Patient", patient_list)
            pt_id = selected_pt.split(" - ")[0]
            
            with st.form("appointment_form"):
                col1, col2 = st.columns(2)
                with col1:
                    app_date = st.date_input("Date", min_value=date.today())
                    app_time = st.time_input("Time")
                with col2:
                    doctor = st.text_input("Doctor Name", "Dr. Sarah Chen")
                    reason = st.text_input("Reason for Visit")
                    
                submitted_appt = st.form_submit_button("Schedule Appointment")
                
                if submitted_appt:
                    appt_data = {
                        'patient_id': pt_id,
                        'appointment_date': str(app_date),
                        'appointment_time': str(app_time),
                        'doctor_name': doctor,
                        'reason': reason,
                        'status': 'Scheduled',
                        'notes': ''
                    }
                    success, msg = backend.add_appointment(appt_data)
                    if success:
                        st.success(f"Success: {msg}")
                    else:
                        st.error(f"Error: {msg}")

if __name__ == "__main__":
    main()
