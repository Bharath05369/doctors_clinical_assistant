import sqlite3
import os
import random
from datetime import datetime, timedelta

DB_NAME = 'clinical_system.db'

def get_db_connection():
    """Get a connection to the database"""
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize the database with tables and synthetic data if empty"""
    # Check if we need to recreate (optional: for now we'll just create if not exists)
    # in a real app better to migrations, but here we just ensure tables exist
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Reset for demo purposes to ensure we get the large dataset
    # c.execute("DROP TABLE IF EXISTS patients")
    # c.execute("DROP TABLE IF EXISTS appointments")
    # c.execute("DROP TABLE IF EXISTS lab_results")
    # c.execute("DROP TABLE IF EXISTS medications")

    # Patients table
    c.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        patient_id TEXT PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        date_of_birth DATE,
        age INTEGER,
        gender TEXT,
        contact_number TEXT,
        email TEXT,
        address TEXT,
        primary_diagnosis TEXT,
        allergies TEXT,
        last_visit DATE
    )
    ''')
    
    # Appointments table
    c.execute('''
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT,
        appointment_date DATE,
        appointment_time TIME,
        doctor_name TEXT,
        reason TEXT,
        status TEXT,
        notes TEXT,
        FOREIGN KEY(patient_id) REFERENCES patients(patient_id)
    )
    ''')
    
    # Medications table
    c.execute('''
    CREATE TABLE IF NOT EXISTS medications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT,
        medication_name TEXT,
        dosage TEXT,
        frequency TEXT,
        start_date DATE,
        end_date DATE,
        status TEXT,
        FOREIGN KEY(patient_id) REFERENCES patients(patient_id)
    )
    ''')

    # Lab Results
    c.execute('''
    CREATE TABLE IF NOT EXISTS lab_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT,
        result_date DATE,
        test_name TEXT,
        value REAL,
        unit TEXT,
        reference_low REAL,
        reference_high REAL,
        interpretation TEXT
    )
    ''')
    
    conn.commit()
    
    # Check if empty, if so, populate synthetic data
    c.execute('SELECT count(*) FROM patients')
    if c.fetchone()[0] == 0:
        print("Empty database detected. Populating synthetic data...")
        populate_synthetic_data(conn)
        
    conn.close()

def populate_synthetic_data(conn):
    """Populate database with large synthetic dataset"""
    print("Generating large synthetic dataset...")
    
    first_names = ['James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda', 'William', 'Elizabeth', 
                   'David', 'Barbara', 'Richard', 'Susan', 'Joseph', 'Jessica', 'Thomas', 'Sarah', 'Charles', 'Karen',
                   'Christopher', 'Nancy', 'Daniel', 'Lisa', 'Matthew', 'Betty', 'Anthony', 'Margaret', 'Mark', 'Sandra']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez',
                  'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin']
    
    diagnoses = ['Type 2 Diabetes', 'Hypertension', 'Coronary Artery Disease', 'Asthma', 'Hyperlipidemia', 
                 'Migraine', 'Osteoarthritis', 'Anxiety Disorder', 'Depression', 'GERD', 'Hypothyroidism', 'None']
    
    allergies_list = ['Penicillin', 'Sulfa', 'Peanuts', 'Latex', 'Dust Mites', 'None', 'None', 'None', 'Adhesive', 'Shellfish']
    
    doctors = ['Dr. Sarah Chen', 'Dr. Amanda Lee', 'Dr. Michael Rodriguez', 'Dr. James Wilson', 'Dr. Emily White']

    patients = []
    appointments = []
    lab_results = []
    medications = []
    
    # Generate 100 patients with 3 years of history (2021-2025)
    start_date = datetime(2021, 1, 1)
    end_date = datetime(2025, 12, 30)
    
    for i in range(1, 101):
        p_id = f'P{i:03d}'
        f_name = random.choice(first_names)
        l_name = random.choice(last_names)
        
        random.seed(p_id) 
        
        year = random.randint(1950, 2000)
        dob = f"{year}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        age = 2024 - year
        gender = random.choice(['M', 'F'])
        diagnosis = random.choice(diagnoses)
        allergy = random.choice(allergies_list)
        
        # Helper to generate date
        def get_date(start_year, end_year):
            y = random.randint(start_year, end_year)
            m = random.randint(1, 12)
            d = random.randint(1, 28)
            return datetime(y, m, d).strftime('%Y-%m-%d')

        # Medication Logic based on Diagnosis - Enhanced
        # Rule: 2024-2025 = Active, 2021-2023 = Discontinued/History
        
        # Consistent logic: 
        # If we generate a date in 2024-2025 -> Status = Active, End Date = None
        # If we generate a date in 2021-2023 -> Status = Discontinued, End Date = some date after start
        
        def add_med(name, dosage, freq, forced_status=None):
            # If forced_status is provided, we use it to determine the date range
            # If not, we randomize
            
            if forced_status == 'Active':
                is_active = True
            elif forced_status == 'Discontinued':
                is_active = False
            else:
                is_active = random.random() < 0.7 # Default random chance

            if is_active:
                start = get_date(2024, 2025)
                medications.append((p_id, name, dosage, freq, start, None, 'Active'))
            else:
                start_year = random.randint(2021, 2023)
                start = get_date(start_year, start_year)
                # End date 3-12 months later
                end_date_obj = datetime.strptime(start, '%Y-%m-%d') + timedelta(days=random.randint(90, 365))
                end = end_date_obj.strftime('%Y-%m-%d')
                medications.append((p_id, name, dosage, freq, start, end, 'Discontinued'))

        if diagnosis == 'Type 2 Diabetes':
            add_med('Metformin', '1000mg', 'Twice daily', forced_status='Active') 
            add_med('Glipizide', '5mg', 'Daily', forced_status='Discontinued')
            add_med('Sitagliptin', '100mg', 'Daily') # Random
            
        elif diagnosis == 'Hypertension':
            add_med('Lisinopril', '10mg', 'Daily', forced_status='Active')
            add_med('Amlodipine', '5mg', 'Daily', forced_status='Discontinued')
            add_med('Hydrochlorothiazide', '25mg', 'Daily')
            
        elif diagnosis == 'Asthma':
            add_med('Albuterol Inhaler', '90mcg', 'As needed', forced_status='Active')
            add_med('Fluticasone', '110mcg', 'Twice daily', forced_status='Discontinued')
            add_med('Montelukast', '10mg', 'Daily')
            
        elif diagnosis == 'Hyperlipidemia':
            add_med('Atorvastatin', '20mg', 'Daily', forced_status='Active')
            add_med('Simvastatin', '40mg', 'Daily', forced_status='Discontinued') 
            
        elif diagnosis == 'Coronary Artery Disease':
            add_med('Aspirin', '81mg', 'Daily', forced_status='Active')
            add_med('Metoprolol', '25mg', 'Daily', forced_status='Discontinued')
            add_med('Clopidogrel', '75mg', 'Daily')
            
        elif diagnosis == 'Anxiety Disorder':
            add_med('Sertraline', '50mg', 'Daily', forced_status='Active')
            add_med('Lorazepam', '0.5mg', 'As needed', forced_status='Discontinued')
            
        elif diagnosis == 'Depression':
            add_med('Fluoxetine', '20mg', 'Daily', forced_status='Active')
            add_med('Bupropion', '150mg', 'Daily', forced_status='Discontinued')
            
        elif diagnosis == 'Hypothyroidism':
            add_med('Levothyroxine', '50mcg', 'Daily', forced_status='Active')
            # Fake a discontinued dose change
            add_med('Levothyroxine', '25mcg', 'Daily', forced_status='Discontinued')
            
        elif diagnosis == 'GERD':
            add_med('Omeprazole', '20mg', 'Daily', forced_status='Active')
            add_med('Famotidine', '20mg', 'Twice daily', forced_status='Discontinued')
            
        elif diagnosis == 'Migraine':
            add_med('Sumatriptan', '50mg', 'As needed', forced_status='Active')
            add_med('Topiramate', '25mg', 'Daily', forced_status='Discontinued')
        
        # Random History Antibiotics (Discontinued)
        if random.random() < 0.5:
            start_year = random.randint(2021, 2023)
            start = get_date(start_year, start_year)
            end = (datetime.strptime(start, '%Y-%m-%d') + timedelta(days=7)).strftime('%Y-%m-%d')
            medications.append((p_id, 'Amoxicillin', '500mg', 'Three times daily', start, end, 'Discontinued'))
            
        if random.random() < 0.3:
            start_year = random.randint(2021, 2022)
            start = get_date(start_year, start_year)
            end = (datetime.strptime(start, '%Y-%m-%d') + timedelta(days=5)).strftime('%Y-%m-%d')
            medications.append((p_id, 'Azithromycin', '250mg', 'Daily', start, end, 'Discontinued'))

        # Last visit will be updated to most recent generated appointment
        last_visit = '2021-01-01'
        
        # Generate History: Iterate month by month from 2021
        # Generate History: Guarantee visits for each year 2021-2025
        for year in range(2021, 2026):
            # 3-5 visits per year to ensure dense data
            num_visits = random.randint(3, 5)
            
            # Generate random dates for this year
            visit_dates = []
            for _ in range(num_visits):
                visit_dates.append(datetime(year, random.randint(1, 12), random.randint(1, 28)))
            
            # Sort dates so they are chronological
            visit_dates.sort()
            
            for visit_date in visit_dates:
                # Create Appointment
                appt_date_str = visit_date.strftime('%Y-%m-%d')
                last_visit = appt_date_str
                
                # Check against end_date to mark as Completed
                status = 'Completed' if visit_date <= end_date else 'Scheduled'
                
                reason = "Routine Checkup"
                if diagnosis != 'None' and random.random() < 0.5:
                    reason = f"{diagnosis} Follow-up"
                
                appointments.append((
                    p_id, appt_date_str, f"{random.randint(9,16)}:00",
                    random.choice(doctors), reason, status, "Routine notes"
                ))
                
                # Generate Labs for this visit (if Completed)
                if status == 'Completed':
                    # Common Panels (CBC, CMP elements) - Every visit for this dense dataset request
                    # Gluocse
                    val_glc = random.randint(70, 110) if 'Diabetes' not in diagnosis else random.randint(100, 250)
                    lab_results.append((p_id, appt_date_str, 'Glucose', val_glc, 'mg/dL', 70, 100, 'High' if val_glc > 100 else 'Normal'))
                    
                    # Creatinine
                    val_cr = round(random.uniform(0.6, 1.2), 1)
                    lab_results.append((p_id, appt_date_str, 'Creatinine', val_cr, 'mg/dL', 0.6, 1.2, 'Normal'))
                    
                    # Hemoglobin
                    val_hgb = round(random.uniform(12.0, 16.0), 1)
                    lab_results.append((p_id, appt_date_str, 'Hemoglobin', val_hgb, 'g/dL', 12.0, 16.0, 'Normal'))
                    
                    # Blood Pressure (Systolic/Diastolic)
                    is_htn = 'Hypertension' in diagnosis or 'Coronary' in diagnosis
                    val_sys = random.randint(130, 170) if is_htn else random.randint(110, 135)
                    val_dia = random.randint(85, 105) if is_htn else random.randint(70, 85)
                    
                    lab_results.append((p_id, appt_date_str, 'BP Systolic', val_sys, 'mmHg', 90, 120, 'High' if val_sys > 120 else 'Normal'))
                    lab_results.append((p_id, appt_date_str, 'BP Diastolic', val_dia, 'mmHg', 60, 80, 'High' if val_dia > 80 else 'Normal'))
                    
                    # Lipid Panel
                    is_bad_lipids = 'Hyperlipidemia' in diagnosis or 'Coronary' in diagnosis or 'Diabetes' in diagnosis
                    
                    val_ldl = random.randint(130, 190) if is_bad_lipids else random.randint(70, 129)
                    lab_results.append((p_id, appt_date_str, 'LDL Cholesterol', val_ldl, 'mg/dL', 0, 100, 'High' if val_ldl > 100 else 'Normal'))
                    
                    val_hdl = random.randint(30, 50) if is_bad_lipids else random.randint(40, 80)
                    lab_results.append((p_id, appt_date_str, 'HDL Cholesterol', val_hdl, 'mg/dL', 40, 100, 'Low' if val_hdl < 40 else 'Normal'))
                    
                    val_trig = random.randint(150, 350) if is_bad_lipids else random.randint(50, 149)
                    lab_results.append((p_id, appt_date_str, 'Triglycerides', val_trig, 'mg/dL', 0, 150, 'High' if val_trig > 150 else 'Normal'))

                    # Kidney Function (BUN)
                    val_bun = random.randint(7, 20)
                    lab_results.append((p_id, appt_date_str, 'BUN', val_bun, 'mg/dL', 7, 20, 'Normal'))

                    # Specific Condition Labs
                    if 'Diabetes' in diagnosis or random.random() < 0.3:
                        val_a1c = round(random.uniform(6.0, 9.0), 1) if 'Diabetes' in diagnosis else round(random.uniform(4.5, 5.6), 1)
                        lab_results.append((p_id, appt_date_str, 'HbA1c', val_a1c, '%', 4.0, 5.7, 'High' if val_a1c > 6.5 else 'Normal'))

        patients.append((
            p_id, f_name, l_name, dob, age, gender, 
            f'555-{random.randint(1000,9999)}', 
            f'{f_name.lower()}.{l_name.lower()}@example.com',
            f'123 Main St', # Simplified address
            diagnosis, allergy, last_visit
        ))
                
    # Reset seed
    random.seed()
    
    conn.executemany('''
    INSERT INTO patients VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    ''', patients)
    
    conn.executemany('''
    INSERT INTO appointments (patient_id, appointment_date, appointment_time, doctor_name, reason, status, notes)
    VALUES (?,?,?,?,?,?,?)
    ''', appointments)
    
    conn.executemany('''
    INSERT INTO medications (patient_id, medication_name, dosage, frequency, start_date, end_date, status)
    VALUES (?,?,?,?,?,?,?)
    ''', medications)
    
    conn.executemany('''
    INSERT INTO lab_results (patient_id, result_date, test_name, value, unit, reference_low, reference_high, interpretation)
    VALUES (?,?,?,?,?,?,?,?)
    ''', lab_results)

    conn.commit()
    print(f"✅ Generated {len(patients)} patients, {len(appointments)} appointments, {len(medications)} medications, and {len(lab_results)} lab results.")
