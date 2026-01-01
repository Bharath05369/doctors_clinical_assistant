# Clinical RAG Chatbot

A comprehensive "Doctor's Clinical Assistant" designed to serve as a second brain for physicians. This system manages patient records, visualizes medical history, and uses a RAG-enhanced AI to answer clinical queries.

## 🚀 Key Features

### 1. Longitudinal Patient Records
-   **Guaranteed Data (2021-2025)**: The system automatically generates comprehensive synthetic records (labs & appointments) for every year from 2021 to 2025.
-   **No Gaps**: Ensures robust data availability for trend analysis.

### 2. Intelligent AI Assistant (RAG)
-   **Natural Language Queries**: Ask questions like *"Show me the glucose trend for the last 3 years"*.
-   **Dynamic Date Parsing**: Understands any time range (e.g., "Last 4 years", "Last 18 months").
-   **Full History Visibility**: Retrieves and displays up to 100 relevant records, sorted **Newest First** (2025 -> 2021).

### 3. Interactive Dashboard
-   **Visual Trends**: Plotly charts for lab results.
-   **Appointment Search**: Filter appointments by Date, Doctor, or Status instantly.

## 📂 Project Structure

-   **`app.py`**: Main application entry point.
-   **`database.py`**: Handles SQLite connection, schema, and synthetic data generation.
-   **`backend.py`**: Contains business logic, query processing, and RAG implementation.
-   **`pages/`**:
    -   `1_Analysis_Dashboard.py`: Main doctor interface for analysis.
    -   `2_Add_Records.py`: Form to add new patients/appointments.
-   **`clinical_system.db`**: SQLite database (generated automatically).

## 🛠️ How to Run

1.  **Install Dependencies** (if needed):
    ```bash
    pip install streamlit pandas plotly
    ```

2.  **Run the App**:
    ```bash
    streamlit run app.py
    ```

3.  **Access**: Open the URL shown in the terminal (usually `http://localhost:8501`).

## 💾 Data Persistence
-   The database `clinical_system.db` is created in the project folder.
-   It is **persistent**: Restarting the app will **NOT** delete your data unless you manually delete this file.
-   Patient lists are sorted by ID for consistent ordering.
