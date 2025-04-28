# Chicago Crime Dashboard

An **interactive Streamlit dashboard** for analyzing and visualizing crime data in **Chicago (2012–2017)**, built after a complete **ETL (Extract, Transform, Load)** process with **feature engineering** and **automation pipelines**.

---

## 📂 Project Structure

```
Chicago-Crime-Dashboard/
│
├── ETL_Script.py                     # ETL and Feature Engineering automation
├── Crime data ETL.ipynb              # Data cleaning & ETL
├── Cleaned_Crimes_in_Chicago.csv     # Processed and cleaned dataset
├── crimes_cleaned.db                 # SQLite database
├── app.py                            # Streamlit dashboard source code
├── README.md                         # Project documentation
├── Data Chicago Crime                # Dataset 2011-2017
└── requirements.txt                  # Required Python packages
```

---

## 🛠️ 1. ETL & Feature Engineering

This project processes the "Crimes in Chicago (2001–2017)" dataset through a complete ETL pipeline.

**Steps performed:**

### Data Cleaning:
- Removed duplicate records.
- Dropped rows with missing or invalid coordinates (Latitude, Longitude).
- Standardized categorical columns (Primary Type, Location Description).
- Normalized timestamps into Year, Month, Day, Hour, and Weekday.

### Feature Engineering:
- **Is_Weekend**: Flagged whether the incident occurred on a weekend.
- **Season**: Determined the season based on the month.
- **Crime Severity Score**: Assigned a score (1–5) to each crime type based on severity.
- **Spatial Density**: Number of incidents per community area (for future spatial analysis).
- **Rolling 7-Day Average**: Calculated moving averages of crime occurrences over time.

### Normalized Tables Created:
- **Incidents Table**: Main table with enriched crime records.
- **Crime_Types Table**: Table containing unique crime types and their descriptions.
- **Locations Table**: Table with unique locations, community areas, and coordinates.

### Data Reshaping:
- **Unpivoted Crime Counts**: Flat structure showing Year, Month, Primary Type, and Count.
- **Pivoted Monthly Summary**: Monthly crime summaries useful for trend analysis.

---

## 🤖 2. Pipeline Automation

The entire ETL and feature engineering workflow is automated through a **Python script**.

**Pipeline Stages:**
- Load raw CSV data.
- Clean and standardize data.
- Engineer additional features.
- Normalize into separate tables.
- Save outputs (CSV files and SQLite database).
- Reshape data for analytical dashboards.

**Automation Highlights:**
- **Parameterized Inputs**: Easily modify paths and filenames.
- **Folder Management**: Automatically creates missing output folders.
- **Database Ready**: Final cleaned dataset stored in an SQLite database (`crimes_cleaned.db`).
- **Logging**: Step-by-step progress messages during the automation process.

---

## 🧠 3. How to Run the ETL Pipeline

**Requirements:**
- Python 3.7+
- Libraries: `pandas`, `numpy`, `sqlite3` (built-in)

**Steps:**
1. Place the input file `chicago_crimes.csv` in the project directory.
2. Install required libraries if not already installed:
   ```bash
   pip install pandas numpy
   ```
3. Run the automation script:
   ```bash
   python Automation_Script.py
   ```

The script will create:
- Processed CSV file (`Cleaned_Crimes_in_Chicago.csv`)
- SQLite database (`crimes_cleaned.db`)  
- Reshaped analytical tables

---

## 📊 4. Dashboard Features

The Streamlit dashboard provides a detailed exploration of Chicago crime data.

**Features include:**
- **Key Metrics**:
  - Total crimes reported
  - Arrests made
  - Most common crime type
  - Top community area for crimes
  - Weekend and domestic crime rates

- **Interactive Filters**:
  - Filter by year, crime type, time of day
  - Aggregations: Hourly, Weekly, Monthly, Yearly

- **Tabs (Pages)**:
  - 📈 **Time-Based Crime Analysis**
  - 🔍 **Crime Type vs Arrest Rate**
  - 🌡️ **Arrest Heatmaps**
  - 📉 **Crime Severity vs Arrest Rate**
  - 🗺️ **Crime Density Map**
  - 🏆 **Crime Leaderboard** (Planned)

- **Data Download**:
  - Export any analysis data as CSV

---

## ⚙️ Setup Instructions (for Dashboard)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/Chicago-Crime-Dashboard.git
   cd Chicago-Crime-Dashboard
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip freeze > requirements.txt
   ```

4. **Run the Streamlit app**:
   ```bash
   streamlit run app.py
   ```

---

## 🚀 Future Enhancements

- Implement **predictive models** (crime forecasting).
- Deploy online via **Streamlit Cloud** or **AWS EC2**.

---

## 📜 License

This project is licensed under the **MIT License** — feel free to fork, modify, and use.

---

## 🙌 Acknowledgements

- Chicago Open Data Portal for providing the crime datasets.
- Streamlit and Plotly for empowering data storytelling.

---
