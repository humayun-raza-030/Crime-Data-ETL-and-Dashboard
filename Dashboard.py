import streamlit as st

# Set page config must be the first Streamlit command
st.set_page_config(page_title="Chicago Crime Dashboard", layout="wide")

import pandas as pd
import plotly.express as px
import numpy as np
import io

# Load Processed Data with sampling to reduce memory usage
@st.cache_data
def load_data():
    full_df = pd.read_csv(r'C:\Users\Humayun\Dashboard\Cleaned_Crimes_in_Chicago.csv', parse_dates=['Date'])
    # Use 70% of the data to reduce memory usage
    sampled_df = full_df.sample(frac=0.5, random_state=42)
    return sampled_df

# Helper function to convert dataframe to CSV for download
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

df = load_data()

# Streamlit Page Setup - Title and caption
st.title("Chicago Crime Dashboard (2012-2017)")
st.caption("Note: Using 50% of data sample to prevent memory issues")

# Severity Mapping
severity_mapping = {
    'ARSON': 4, 'ASSAULT': 4, 'BATTERY': 4, 'BURGLARY': 3,
    'CONCEALED CARRY LICENSE VIOLATION': 2, 'CRIM SEXUAL ASSAULT': 5,
    'CRIMINAL DAMAGE': 3, 'CRIMINAL TRESPASS': 1, 'DECEPTIVE PRACTICE': 3,
    'GAMBLING': 2, 'HOMICIDE': 5, 'HUMAN TRAFFICKING': 5,
    'INTERFERENCE WITH PUBLIC OFFICER': 2, 'INTIMIDATION': 1,
    'KIDNAPPING': 5, 'LIQUOR LAW VIOLATION': 2, 'MOTOR VEHICLE THEFT': 3,
    'NARCOTICS': 3, 'NON - CRIMINAL': 1, 'NON-CRIMINAL': 1,
    'NON-CRIMINAL (SUBJECT SPECIFIED)': 1, 'OBSCENITY': 2,
    'OFFENSE INVOLVING CHILDREN': 1, 'OTHER NARCOTIC VIOLATION': 2,
    'OTHER OFFENSE': 2, 'PROSTITUTION': 2, 'PUBLIC INDECENCY': 1,
    'PUBLIC PEACE VIOLATION': 2, 'ROBBERY': 4, 'SEX OFFENSE': 1,
    'STALKING': 1, 'THEFT': 3, 'WEAPONS VIOLATION': 4
}
df['Crime_Severity_Score'] = df['Primary Type'].map(severity_mapping).fillna(1)

# Sidebar Filters
st.sidebar.header("Filters")

# Year Range Selector - Default to 2017
show_all_years = st.sidebar.checkbox("Show All Years (2012-2017)", value=False)

if show_all_years:
    df_filtered = df.copy()
else:
    year_min = int(df['Year'].min())
    year_max = int(df['Year'].max())
    # Set default to 2017
    selected_year = st.sidebar.slider(
        "Select Year Range", 
        min_value=year_min, 
        max_value=year_max, 
        value=(2017, 2017)  # Default to 2017 specifically
    )
    start_year, end_year = selected_year
    df_filtered = df[(df['Year'] >= start_year) & (df['Year'] <= end_year)]

# Other Filters
crime_types = list(df['Primary Type'].unique())
crime_type_options = ["All"] + crime_types  # Add "All" as the first option

selected_crime = st.sidebar.selectbox("Select Crime Type", options=crime_type_options, index=0)  # Default to "All"

time_of_day = st.sidebar.radio("Select Time of Day", options=["All", "Morning", "Afternoon", "Evening", "Night"])
time_period = st.sidebar.selectbox("Select Time Period", options=["Hourly", "Weekly", "Monthly", "Yearly"])

# Apply Crime Type Filter
if selected_crime == "All":
    df_filtered = df_filtered  # Keep all crime types
else:
    df_filtered = df_filtered[df_filtered['Primary Type'] == selected_crime]  # Filter for specific crime type

# Apply Time of Day Filter
if time_of_day != "All":
    df_filtered['Time_of_Day'] = df_filtered['Date'].dt.hour.apply(
        lambda x: "Morning" if 6 <= x < 12 else ("Afternoon" if 12 <= x < 18 else ("Evening" if 18 <= x < 24 else "Night"))
    )
    df_filtered = df_filtered[df_filtered['Time_of_Day'] == time_of_day]


# Tabs
tab2, tab3, tab4, tab5, tab6, tab8 = st.tabs([ 
    "Time-based Analysis", 
    "Crime Type vs Arrest", 
    "Arrest Heatmap", 
    "Crime Severity & Arrest Rate", 
    "Crime Density Map", 
    "Crime Leaderboard"
])

# 1. Key Metrics



total_crimes = df_filtered.shape[0]
total_arrests = df_filtered['Arrest'].sum()
most_frequent_crime = df_filtered['Primary Type'].value_counts().idxmax()
most_common_area = df_filtered['Community Area'].value_counts().idxmax()

df_filtered['Day_of_Week'] = df_filtered['Date'].dt.dayofweek
weekend_crimes = df_filtered[df_filtered['Day_of_Week'] >= 5]
percentage_weekend_crimes = (weekend_crimes.shape[0] / df_filtered.shape[0]) * 100

domestic_crimes = df_filtered[df_filtered['Description'].str.contains('DOMESTIC', case=False, na=False)]
percentage_domestic_crimes = (domestic_crimes.shape[0] / df_filtered.shape[0]) * 100



# 2. Time-based Analysis
with tab2:
    st.header("Key Metrics")
    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
    with kpi1:
        st.metric("Total Crimes Reported", total_crimes)
    with kpi2:
        st.metric("Total Arrests Made", total_arrests)
    with kpi3:
        st.metric("Most Frequent Crime Type", most_frequent_crime)
    with kpi4:
        st.metric("Community Area with Most Crimes", most_common_area)
    with kpi5:
        st.metric("% Crimes on Weekend", f"{round(percentage_weekend_crimes, 2)}%")
    with kpi6:
        st.metric("% Domestic Crimes", f"{round(percentage_domestic_crimes, 2)}%")

    st.divider()

    if time_period == "Hourly":
        df_filtered['Hour'] = df_filtered['Date'].dt.hour
        df_time_grouped = df_filtered.groupby(['Hour', 'Primary Type']).size().reset_index(name='Incidents')
        x_axis = 'Hour'
        title = "Crime Incidents by Hour"
    elif time_period == "Weekly":
        df_filtered['Week'] = df_filtered['Date'].dt.isocalendar().week
        df_time_grouped = df_filtered.groupby(['Week', 'Primary Type']).size().reset_index(name='Incidents')
        x_axis = 'Week'
        title = "Crime Incidents by Week"
    elif time_period == "Monthly":
        df_filtered['Month'] = df_filtered['Date'].dt.month
        df_time_grouped = df_filtered.groupby(['Month', 'Primary Type']).size().reset_index(name='Incidents')
        x_axis = 'Month'
        title = "Crime Incidents by Month"
    else:
        df_time_grouped = df_filtered.groupby(['Year', 'Primary Type']).size().reset_index(name='Incidents')
        x_axis = 'Year'
        title = "Crime Incidents by Year"

    st.header(title)
    fig_time = px.line(
        df_time_grouped, x=x_axis, y='Incidents', color='Primary Type',
        markers=True, title=title
    )
    fig_time.update_layout(hovermode="x unified")
    st.plotly_chart(fig_time, use_container_width=True)
    
    # Add download button for time-based analysis data
    time_csv = convert_df_to_csv(df_time_grouped)
    st.download_button(
        label="Download Time-based Analysis Data",
        data=time_csv,
        file_name=f'crime_data_by_{time_period.lower()}.csv',
        mime='text/csv',
    )

# 3. Comparative Analysis (Crime Type and Arrest)
with tab3:

    st.header("Key Metrics")
    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
    with kpi1:
        st.metric("Total Crimes Reported", total_crimes)
    with kpi2:
        st.metric("Total Arrests Made", total_arrests)
    with kpi3:
        st.metric("Most Frequent Crime Type", most_frequent_crime)
    with kpi4:
        st.metric("Community Area with Most Crimes", most_common_area)
    with kpi5:
        st.metric("% Crimes on Weekend", f"{round(percentage_weekend_crimes, 2)}%")
    with kpi6:
        st.metric("% Domestic Crimes", f"{round(percentage_domestic_crimes, 2)}%")

    st.divider()

    st.header("Comparative Analysis")


    col1, col2 = st.columns(2)
    with col1:
        crime_type_dist = df_filtered['Primary Type'].value_counts().reset_index()
        crime_type_dist.columns = ['Crime Type', 'Incidents']
        fig_pie_crime_type = px.pie(crime_type_dist, names='Crime Type', values='Incidents', title="Distribution of Crime Types")
        st.plotly_chart(fig_pie_crime_type, use_container_width=True)

    with col2:
        arrest_dist = df_filtered['Arrest'].value_counts().reset_index()
        arrest_dist.columns = ['Arrest Status', 'Incidents']
        fig_pie_arrest = px.pie(arrest_dist, names='Arrest Status', values='Incidents', 
                                title="Arrest vs Non-Arrest Distribution", 
                                color_discrete_map={True: 'green', False: 'red'})
        st.plotly_chart(fig_pie_arrest, use_container_width=True)
        
    # Add download buttons for crime type and arrest data
    crime_type_csv = convert_df_to_csv(crime_type_dist)
    st.download_button(
        label="Download Crime Type Distribution Data",
        data=crime_type_csv,
        file_name='crime_type_distribution.csv',
        mime='text/csv',
    )
    
    arrest_csv = convert_df_to_csv(arrest_dist)
    st.download_button(
        label="Download Arrest Distribution Data",
        data=arrest_csv,
        file_name='arrest_distribution.csv',
        mime='text/csv',
    )

# 4. Arrest Heatmap
with tab4:

    st.header("Key Metrics")
    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
    with kpi1:
        st.metric("Total Crimes Reported", total_crimes)
    with kpi2:
        st.metric("Total Arrests Made", total_arrests)
    with kpi3:
        st.metric("Most Frequent Crime Type", most_frequent_crime)
    with kpi4:
        st.metric("Community Area with Most Crimes", most_common_area)
    with kpi5:
        st.metric("% Crimes on Weekend", f"{round(percentage_weekend_crimes, 2)}%")
    with kpi6:
        st.metric("% Domestic Crimes", f"{round(percentage_domestic_crimes, 2)}%")

    st.divider()

    st.header("Arrest Heatmap by Time of Day & Location Type")
    
    df_filtered['Time_of_Day'] = df_filtered['Date'].dt.hour.apply(
        lambda hour: "Morning" if 6 <= hour < 12 else ("Afternoon" if 12 <= hour < 18 else ("Evening" if 18 <= hour < 24 else "Night"))
    )
    
    # Generate crosstab and handle potential string representation of boolean values
    df_arrest_heatmap = pd.crosstab([df_filtered['Time_of_Day'], df_filtered['Location Description']], df_filtered['Arrest'])
    
    # Convert boolean column names to strings to avoid KeyError with .loc
    df_arrest_heatmap.columns = df_arrest_heatmap.columns.astype(str)
    
    # Calculate arrest rate safely using string keys
    if 'True' in df_arrest_heatmap.columns and 'False' in df_arrest_heatmap.columns:
        df_arrest_heatmap['Arrest Rate'] = df_arrest_heatmap['True'] / (df_arrest_heatmap['True'] + df_arrest_heatmap['False']) * 100
    else:
        # Initialize 'Arrest Rate' column
        df_arrest_heatmap['Arrest Rate'] = 0
        
        # Find the column names that represent True and False values
        true_cols = [col for col in df_arrest_heatmap.columns if col in ('True', '1', 'true')]
        false_cols = [col for col in df_arrest_heatmap.columns if col in ('False', '0', 'false')]
        
        if true_cols and false_cols:
            true_col = true_cols[0]
            false_col = false_cols[0]
            
            # Calculate arrest rate for each row
            for idx in df_arrest_heatmap.index:
                true_val = df_arrest_heatmap.at[idx, true_col]
                false_val = df_arrest_heatmap.at[idx, false_col]
                total = true_val + false_val
                df_arrest_heatmap.at[idx, 'Arrest Rate'] = (true_val / total * 100) if total > 0 else 0
    
    # Create pivot table for visualization
    pivot_table = df_arrest_heatmap.reset_index().pivot_table(
        index='Time_of_Day', 
        columns='Location Description', 
        values='Arrest Rate'
    )
    
    # Visualize the heatmap with increased height
    fig_heatmap = px.imshow(
        pivot_table,
        labels={'color': 'Arrest Rate (%)'},
        title="Arrest Heatmap by Time of Day & Location"
    )
    fig_heatmap.update_layout(height=800)  # Increase height to make it bigger
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Add download button for arrest heatmap data
    df_arrest_heatmap_reset = df_arrest_heatmap.reset_index()
    arrest_heatmap_csv = convert_df_to_csv(df_arrest_heatmap_reset)
    st.download_button(
        label="Download Arrest Heatmap Data",
        data=arrest_heatmap_csv,
        file_name='arrest_heatmap_data.csv',
        mime='text/csv',
    )

# 5. Crime Severity & Arrest Rate
with tab5:

    st.header("Key Metrics")
    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
    with kpi1:
        st.metric("Total Crimes Reported", total_crimes)
    with kpi2:
        st.metric("Total Arrests Made", total_arrests)
    with kpi3:
        st.metric("Most Frequent Crime Type", most_frequent_crime)
    with kpi4:
        st.metric("Community Area with Most Crimes", most_common_area)
    with kpi5:
        st.metric("% Crimes on Weekend", f"{round(percentage_weekend_crimes, 2)}%")
    with kpi6:
        st.metric("% Domestic Crimes", f"{round(percentage_domestic_crimes, 2)}%")

    st.divider()


    st.header("Crime Severity & Arrest Rate by Crime Type")

    col3, col4 = st.columns(2)
    with col3:
        severity_by_crime = df_filtered.groupby('Primary Type')['Crime_Severity_Score'].mean().reset_index()
        fig_severity = px.bar(severity_by_crime, x='Primary Type', y='Crime_Severity_Score',
                              title="Crime Severity by Type", color='Crime_Severity_Score', color_continuous_scale='Viridis')
        st.plotly_chart(fig_severity, use_container_width=True)

    with col4:
        arrest_rate = df_filtered.groupby('Primary Type').agg({'Arrest': 'mean'}).reset_index()
        arrest_rate['Arrest Rate'] = arrest_rate['Arrest'] * 100
        fig_arrest_rate = px.bar(arrest_rate, x='Primary Type', y='Arrest Rate',
                                 title="Arrest Rate by Crime Type", color='Primary Type')
        st.plotly_chart(fig_arrest_rate, use_container_width=True)
        
    # Add download buttons for severity and arrest rate data
    severity_csv = convert_df_to_csv(severity_by_crime)
    st.download_button(
        label="Download Crime Severity Data",
        data=severity_csv,
        file_name='crime_severity_by_type.csv',
        mime='text/csv',
    )
    
    arrest_rate_csv = convert_df_to_csv(arrest_rate)
    st.download_button(
        label="Download Arrest Rate Data",
        data=arrest_rate_csv,
        file_name='arrest_rate_by_crime_type.csv',
        mime='text/csv',
    )

# 6. Crime Density Map
with tab6:

    st.header("Key Metrics")
    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
    with kpi1:
        st.metric("Total Crimes Reported", total_crimes)
    with kpi2:
        st.metric("Total Arrests Made", total_arrests)
    with kpi3:
        st.metric("Most Frequent Crime Type", most_frequent_crime)
    with kpi4:
        st.metric("Community Area with Most Crimes", most_common_area)
    with kpi5:
        st.metric("% Crimes on Weekend", f"{round(percentage_weekend_crimes, 2)}%")
    with kpi6:
        st.metric("% Domestic Crimes", f"{round(percentage_domestic_crimes, 2)}%")

    st.divider()


    st.header("Crime Density Heatmap by Location")
    
    df_map = df_filtered.dropna(subset=['Latitude', 'Longitude'])
    
    fig_density = px.density_mapbox(
        df_map, lat='Latitude', lon='Longitude', radius=10,
        center=dict(lat=41.8781, lon=-87.6298), zoom=9,
        mapbox_style="open-street-map", title="Crime Density Heatmap",
        color_continuous_scale="Greens", opacity=0.5,
    )
    st.plotly_chart(fig_density, use_container_width=True)

    st.header("Location and Arrest Pattern Correlation")
    
    # Crosstab of Location Description vs Arrest Status
    df_loc_arrest = pd.crosstab(df_filtered['Location Description'], df_filtered['Arrest'])

    # Dynamically determine the correct keys
    arrest_true_key = True if True in df_loc_arrest.columns else "True" if "True" in df_loc_arrest.columns else None
    arrest_false_key = False if False in df_loc_arrest.columns else "False" if "False" in df_loc_arrest.columns else None

    # Initialize Arrest Rate
    df_loc_arrest['Arrest Rate'] = 0

    # Safely calculate Arrest Rate
    for idx in df_loc_arrest.index:
        true_val = df_loc_arrest.loc[idx, arrest_true_key] if arrest_true_key in df_loc_arrest.columns else 0
        false_val = df_loc_arrest.loc[idx, arrest_false_key] if arrest_false_key in df_loc_arrest.columns else 0
        total = true_val + false_val
        df_loc_arrest.loc[idx, 'Arrest Rate'] = (true_val / total) * 100 if total > 0 else 0

    fig_loc_arrest = px.scatter(df_loc_arrest, x=df_loc_arrest.index, y='Arrest Rate',
                                title="Location vs Arrest Rate", labels={'x': 'Location', 'y': 'Arrest Rate (%)'})
    st.plotly_chart(fig_loc_arrest, use_container_width=True)
    
    # Add download buttons for location data
    loc_arrest_csv = convert_df_to_csv(df_loc_arrest.reset_index())
    st.download_button(
        label="Download Location vs Arrest Rate Data",
        data=loc_arrest_csv,
        file_name='location_arrest_rate.csv',
        mime='text/csv',
    )
    
    # Option to download map data sample (could be large)
    map_data_sample = df_map[['Latitude', 'Longitude', 'Primary Type', 'Location Description']].sample(min(5000, len(df_map)))
    map_data_csv = convert_df_to_csv(map_data_sample)
    st.download_button(
        label="Download Map Data Sample",
        data=map_data_csv,
        file_name='crime_map_data_sample.csv',
        mime='text/csv',
    )

# 8. Crime Leaderboard
with tab8:


    st.header("Key Metrics")
    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
    with kpi1:
        st.metric("Total Crimes Reported", total_crimes)
    with kpi2:
        st.metric("Total Arrests Made", total_arrests)
    with kpi3:
        st.metric("Most Frequent Crime Type", most_frequent_crime)
    with kpi4:
        st.metric("Community Area with Most Crimes", most_common_area)
    with kpi5:
        st.metric("% Crimes on Weekend", f"{round(percentage_weekend_crimes, 2)}%")
    with kpi6:
        st.metric("% Domestic Crimes", f"{round(percentage_domestic_crimes, 2)}%")

    st.divider()

    st.header("Crime Frequency Leaderboard")
    
    col5, col6 = st.columns(2)
    with col5:
        crime_counts = df_filtered['Primary Type'].value_counts().reset_index()
        crime_counts.columns = ['Primary Type', 'Count']
        fig_leaderboard = px.bar(crime_counts, x='Primary Type', y='Count', 
                                 color='Primary Type', title=f"Crime Leaderboard - {selected_year[0]}-{selected_year[1]}")
        fig_leaderboard.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_leaderboard, use_container_width=True)

    with col6:
        df_top_crimes = df_filtered.groupby('Primary Type').size().reset_index(name='Incidents').sort_values(by='Incidents', ascending=False).head(10)
        fig_top10 = px.bar(df_top_crimes, x='Primary Type', y='Incidents',
                           color='Primary Type', title="Top 10 Common Crime Types")
        fig_top10.update_layout(xaxis_tickangle=-45, showlegend=False)
        st.plotly_chart(fig_top10, use_container_width=True)
        
    # Add download button for crime leaderboard data
    crime_counts_csv = convert_df_to_csv(crime_counts)
    st.download_button(
        label="Download Crime Frequency Data",
        data=crime_counts_csv,
        file_name='crime_frequency_leaderboard.csv',
        mime='text/csv',
    )
    
    top10_csv = convert_df_to_csv(df_top_crimes)
    st.download_button(
        label="Download Top 10 Crimes Data",
        data=top10_csv,
        file_name='top_10_crimes.csv',
        mime='text/csv',
    )

# Add download button for the full filtered dataset at the bottom of the sidebar
st.sidebar.divider()
st.sidebar.header("Export Data")

# Option to download the currently filtered dataset
filtered_data_csv = convert_df_to_csv(df_filtered)
st.sidebar.download_button(
    label="Download Current Filtered Dataset",
    data=filtered_data_csv,
    file_name='filtered_chicago_crime_data.csv',
    mime='text/csv',
    help="Download the current filtered dataset based on your selections"
)
