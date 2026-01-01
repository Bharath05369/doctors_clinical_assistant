import streamlit as st
from database import init_database

st.set_page_config(
    page_title="Clinic Manager",
    page_icon="🏥",
    layout="wide"
)

def main():
    # Initialize DB on first load
    init_database()
    
    from backend import ClinicalBackend
    backend = ClinicalBackend()
    st.markdown(backend.get_styles(), unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.image("C:/Users/Bharath V N/.gemini/antigravity/brain/a8a6404a-1204-4d13-b3ad-c9e97df28f30/professional_doctor_portrait_1767170314467.png", use_container_width=True)
    
    with col2:
        st.markdown('<h1 class="main-header">Doctor\'s Clinical Assistant</h1>', unsafe_allow_html=True)
        st.markdown("""
        <p class="hero-text">
        Welcome to your advanced clinical "second brain." Grounded in real patient data and 
        Augmented Retrieval logic, this assistant helps you minimize hallucinations and 
        maximize diagnostic accuracy.
        </p>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        with st.container():
            st.markdown("### 🚀 Quick Insights")
            st.write("✓ **Trend Analysis**: Statistical tables for HbA1c, BP, and more.")
            st.write("✓ **Medication Guard**: Verified history and status tracking.")
            st.write("✓ **Smart Scheduling**: Natural language search for appointments.")
            
        if st.button("Start Analysis"):
            st.switch_page("pages/1_Analysis_Dashboard.py")
    
    st.info("System fully operational and connected to clinical database.")

if __name__ == "__main__":
    main()
