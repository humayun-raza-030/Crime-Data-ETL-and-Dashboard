# ------------------------------
# Chicago Crimes ETL Pipeline
# ------------------------------

import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime
import os

# ------------------------------
# PARAMETERS
# ------------------------------

INPUT_FILE = r"C:\Users\Humayun\Downloads\Chicago_Crimes_2012_to_2017 (1)\Chicago_Crimes_2012_to_2017.csv"    # Input CSV
# PARAMETERS
DB_FILE = 'crimes_cleaned.db'
OUTPUT_FOLDER = r'C:\Users\Humayun\Competition'
SAVE_TO_DB = True

# Create output folder if it does not exist
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
# ------------------------------
# Chicago Crimes ETL Pipeline
# ------------------------------
# ------------------------------
# FUNCTIONS
# ------------------------------

def load_data(file_path):
    df = pd.read_csv(file_path)
    return df

def clean_data(df):
    # Fix Date column
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Drop missing coordinates
    df = df.dropna(subset=['Latitude', 'Longitude'])
    
    # Standardize Categorical Columns
    df['Primary Type'] = df['Primary Type'].str.upper().str.strip()
    df['Location Description'] = df['Location Description'].str.upper().str.strip()
    
    return df

def feature_engineering(df):
    # Timestamp Features
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Day'] = df['Date'].dt.day
    df['Hour'] = df['Date'].dt.hour
    df['Weekday'] = df['Date'].dt.weekday  # Monday=0, Sunday=6
    
    # Weekend Flag
    df['Is_Weekend'] = df['Weekday'].apply(lambda x: 1 if x >=5 else 0)
    
    # Season of Crime
    def get_season(month):
        if month in [12, 1, 2]:
            return 'Winter'
        elif month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        else:
            return 'Fall'
    df['Season'] = df['Month'].apply(get_season)
    
    # Crime Severity Score
    severity_mapping = {
    'ARSON': 4,
    'ASSAULT': 4,
    'BATTERY': 4,
    'BURGLARY': 3,
    'CONCEALED CARRY LICENSE VIOLATION': 2,
    'CRIM SEXUAL ASSAULT': 5,
    'CRIMINAL DAMAGE': 3,
    'CRIMINAL TRESPASS': 1,
    'DECEPTIVE PRACTICE': 3,
    'GAMBLING': 2,
    'HOMICIDE': 5,
    'HUMAN TRAFFICKING': 5,
    'INTERFERENCE WITH PUBLIC OFFICER': 2,
    'INTIMIDATION': 1,
    'KIDNAPPING': 5,
    'LIQUOR LAW VIOLATION': 2,
    'MOTOR VEHICLE THEFT': 3,
    'NARCOTICS': 3,
    'NON - CRIMINAL': 1,
    'NON-CRIMINAL': 1,
    'NON-CRIMINAL (SUBJECT SPECIFIED)': 1,
    'OBSCENITY': 2,
    'OFFENSE INVOLVING CHILDREN': 1,
    'OTHER NARCOTIC VIOLATION': 2,
    'OTHER OFFENSE': 2,
    'PROSTITUTION': 2,
    'PUBLIC INDECENCY': 1,
    'PUBLIC PEACE VIOLATION': 2,
    'ROBBERY': 4,
    'SEX OFFENSE': 1,
    'STALKING': 1,
    'THEFT': 3,
    'WEAPONS VIOLATION': 4
    }

    df['Crime_Severity_Score'] = df['Primary Type'].map(severity_mapping)

    #Rolling 7 DAYS AVERAGE
    # Sort by Date
    df = df.sort_values('Date')

    # Create a daily incident count
    daily_counts = df.groupby(df['Date'].dt.date).size().reset_index(name='Daily_Incidents')

    # Rolling 7-day average
    daily_counts['Rolling_7D_Avg'] = daily_counts['Daily_Incidents'].rolling(window=7, min_periods=1).mean()

    # Merge rolling average back to incidents
    df = df.merge(daily_counts[['Date', 'Rolling_7D_Avg']], left_on=df['Date'].dt.date, right_on='Date', how='left')

        #spatial density
    # Total number of incidents per Community Area
    community_counts = df.groupby('Community Area').size().reset_index(name='Total_Incidents')

    # Assume average community area size
    avg_area_km2 = df['Community Area'].mean()

    # Calculate spatial density
    community_counts['Spatial_Density'] = community_counts['Total_Incidents'] / avg_area_km2

    # Merge back to Locations
    df = df.merge(community_counts[['Community Area', 'Spatial_Density']], on='Community Area', how='left')

    # Repeat Incidents Probablity
    block_counts = df.groupby('Block').size().reset_index(name='Block_Incidents')

    # Total incidents
    total_incidents = len(df)

    # Probability that a random incident is from a frequently-hit block
    block_counts['Repeat_Incident_Prob'] = block_counts['Block_Incidents'] / total_incidents

    # Merge back to Locations
    df = df.merge(block_counts[['Block', 'Repeat_Incident_Prob']], on='Block', how='left')

    return df

def normalize_tables(df):
    # Locations Table
    locations = df[['Block', 'Location Description', 'Community Area', 'Latitude', 'Longitude', 'Spatial_Density', 'Repeat_Incident_Prob']].drop_duplicates().reset_index(drop=True)
    
    # Crime Types Table
    crime_types = df[['Primary Type', 'Description']].drop_duplicates().reset_index(drop=True)
    
    # Incidents Table
    incidents = df[['ID', 'Case Number', 'Date', 'Block', 'Primary Type', 'Description', 'Arrest', 'Domestic', 'Beat', 'District', 'Ward', 'Community Area', 'Year', 'Month', 'Day', 'Hour', 'Weekday', 'Is_Weekend', 'Season', 'Crime_Severity_Score', 'Rolling_7D_Avg']]
    
    return incidents, locations, crime_types

def save_to_db(incidents, locations, crime_types, db_file):
    conn = sqlite3.connect(db_file)
    incidents.to_sql('Incidents', conn, if_exists='replace', index=False)
    locations.to_sql('Locations', conn, if_exists='replace', index=False)
    crime_types.to_sql('Crime_Types', conn, if_exists='replace', index=False)
    conn.close()

def reshape_data(df):
    # Group by Year, Month, Primary Type
    crime_counts = df.groupby(['Year', 'Month', 'Primary Type']).size().reset_index(name='Crime_Count')
    
    # Pivot
    crime_pivot = crime_counts.pivot_table(index=['Year', 'Month'], columns='Primary Type', values='Crime_Count', fill_value=0)
    crime_pivot = crime_pivot.reset_index()
    
    return crime_counts, crime_pivot

# ------------------------------
# MAIN EXECUTION
# ------------------------------

if __name__ == "__main__":
    print("[INFO] Starting ETL pipeline...")
    
    df = load_data(INPUT_FILE)
    print(f"[INFO] Loaded {len(df)} rows.")
    
    df = clean_data(df)
    print(f"[INFO] Cleaned data. {len(df)} rows remaining.")
    
    df = feature_engineering(df)
    print("[INFO] Feature engineering done.")
    
    incidents, locations, crime_types = normalize_tables(df)
    
    if SAVE_TO_DB:
        save_to_db(incidents, locations, crime_types, DB_FILE)
        print(f"[INFO] Data saved to {DB_FILE}")
    
    crime_counts, crime_pivot = reshape_data(df)
    print("[INFO] Data reshaped for analysis.")
    
    # Save outputs if needed
    incidents.to_csv(f"{OUTPUT_FOLDER}incidents.csv", index=False)
    locations.to_csv(f"{OUTPUT_FOLDER}locations.csv", index=False)
    crime_types.to_csv(f"{OUTPUT_FOLDER}crime_types.csv", index=False)
    crime_counts.to_csv(f"{OUTPUT_FOLDER}crime_counts_unpivot.csv", index=False)
    crime_pivot.to_csv(f"{OUTPUT_FOLDER}crime_monthly_pivot.csv", index=False)
    
    print("[SUCCESS] Pipeline finished successfully!")
