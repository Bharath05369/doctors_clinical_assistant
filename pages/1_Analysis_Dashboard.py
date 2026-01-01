import streamlit as st
import pandas as pd
import plotly.express as px
from backend import ClinicalBackend

st.set_page_config(page_title="Doctor Dashboard", page_icon="🩺", layout="wide")

def main():
    backend = ClinicalBackend()
    st.markdown('<h1 class="main-header">Clinical Interpretation & Analysis</h1>', unsafe_allow_html=True)
    
    # Sidebar Patient Selection
    st.sidebar.header("Patient Selection")
    all_patients = backend.get_all_patients()
    
    if all_patients.empty:
        st.warning("No patients found in database.")
        st.stop()
        
    patient_options = all_patients.apply(
        lambda x: f"{x['patient_id']} - {x['first_name']} {x['last_name']}", axis=1
    )
    selected_option = st.sidebar.selectbox("Select Patient", patient_options)
    patient_id = selected_option.split(" - ")[0]
    
    # Get Data
    patient = backend.get_patient_details(patient_id)
    labs = backend.get_patient_labs(patient_id)
    meds = backend.get_patient_medications(patient_id)
    
    # Display Patient Header
    if patient:
        with st.container():
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Patient", f"{patient['first_name']} {patient['last_name']}")
            col2.metric("Age/Gender", f"{patient['age']} / {patient['gender']}")
            col3.metric("Diagnosis", patient['primary_diagnosis'])
            col4.metric("Last Visit", patient['last_visit'])
            
        st.divider()
        
        # --- AI ASSISTANT (PROMOTED TO MAIN VIEW) ---
        st.markdown("### 🤖 Clinical AI Assistant")
        with st.form("ai_assistant_form", border=False):
            st.info("Ask questions about the patient's history, medications, or lab trends.")
            
            col_q, col_btn = st.columns([4, 1])
            with col_q:
                query = st.text_input("Ask a question about this patient:", placeholder="e.g., 'Show BP trend for last 2 years' or 'Do I have an appointment tomorrow?'")
            with col_btn:
                 # Space for alignment
                 st.write("")
                 st.write("") 
                 submit = st.form_submit_button("Analyze", type="primary")

            if submit and query:
                with st.spinner("Analyzing..."):
                    response = backend.run_analysis_query(query, patient_id)
                    st.markdown(response)

        st.markdown("---")

        # Tabs for Data
        tab1, tab2, tab3 = st.tabs(["📊 Lab Results", "📅 Appointments", "💊 Medications"])
        
        with tab1:
            st.subheader("Lab Results History")
            labs_df = backend.get_patient_labs(patient_id)
            
            if not labs_df.empty:
                # Dropdown for test selection
                test_types = labs_df['test_name'].unique()
                selected_test = st.selectbox("Select Lab Test", test_types)
                
                # Filter Data
                filtered_labs = labs_df[labs_df['test_name'] == selected_test].sort_values('result_date')
                
                # Plot
                fig = px.line(filtered_labs, x='result_date', y='value', markers=True, title=f"{selected_test} Over Time")
                # Add reference lines if available
                if not filtered_labs.empty:
                    low = filtered_labs.iloc[0]['reference_low']
                    high = filtered_labs.iloc[0]['reference_high']
                    if low > 0 or high > 0:
                        fig.add_hline(y=low, line_dash="dash", line_color="green", annotation_text="Low Ref")
                        fig.add_hline(y=high, line_dash="dash", line_color="red", annotation_text="High Ref")
                
                st.plotly_chart(fig, use_container_width=True)
                
                st.subheader("📋 Laboratory History")
                st.dataframe(labs_df.sort_values('result_date', ascending=False), use_container_width=True)
            else:
                st.info("No lab results found.")

        with tab2:
            st.subheader("Appointment History")
            appt_df = backend.get_patient_appointments(patient_id)
            if not appt_df.empty:
                st.dataframe(appt_df[['appointment_date', 'appointment_time', 'doctor_name', 'reason', 'status', 'notes']])
            else:
                st.info("No appointments found.")
                
        with tab3:
            st.header(f"Medications for {patient['first_name']}")
            
            meds_df = backend.get_patient_medications(patient_id)
            
            if not meds_df.empty:
                # Active
                active_meds = meds_df[meds_df['status'] == 'Active']
                if not active_meds.empty:
                    st.subheader(f"✅ Active Prescriptions ({len(active_meds)})")
                    st.dataframe(active_meds[['medication_name', 'dosage', 'frequency', 'start_date']], use_container_width=True, hide_index=True)
                
                # Discontinued
                discontinued_meds = meds_df[meds_df['status'] == 'Discontinued']
                if not discontinued_meds.empty:
                    st.subheader(f"🛑 Discontinued / Past Medications ({len(discontinued_meds)})")
                    st.dataframe(discontinued_meds[['medication_name', 'dosage', 'frequency', 'start_date', 'end_date', 'status']], use_container_width=True, hide_index=True)
            else:
                st.info("No medication records found.")

if __name__ == "__main__":
    main()
