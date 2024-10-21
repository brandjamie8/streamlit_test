import streamlit as st
import pandas as pd
import plotly.express as px

# Section 1 - Data Upload and Manual Entry
st.title("Hospital Theatres Demand and Capacity App")
st.header("Section 1: Procedure Data and Last Year's Capacity")

# Upload File
uploaded_file = st.file_uploader("Upload Procedure Data", type='csv')

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Uploaded data preview:")
    st.dataframe(df)
else:
    st.write("Manually enter procedure data")
    procedures = st.text_area('Enter procedures (comma-separated)', value='Procedure A, Procedure B, Procedure C')
    procedures = procedures.split(',')
    demand = st.text_area('Enter annual demand cases (comma-separated)', value='100, 150, 200')
    demand = list(map(int, demand.split(',')))
    durations = st.text_area('Enter average durations in hours (comma-separated)', value='2.0, 1.5, 1.0')
    durations = list(map(float, durations.split(',')))
    df = pd.DataFrame({
        'Procedure': procedures,
        'Annual Demand (Cases)': demand,
        'Average Duration (Hours)': durations
    })

# Input Last Year's Capacity
st.subheader("Input Last Year's Capacity")
last_year_weeks = st.number_input('Weeks operating last year', value=48)
last_year_sessions = st.number_input('Sessions per week last year', value=10)
last_year_utilization = st.slider('Utilization Percentage', min_value=0.0, max_value=1.0, value=0.80, step=0.05)
session_duration = st.number_input('Session Duration (Hours)', value=4)

# Calculate total demand hours
df['Total Demand (Hours)'] = df['Annual Demand (Cases)'] * df['Average Duration (Hours)']
total_demand_hours = df['Total Demand (Hours)'].sum()

# Section 2 - Demand Treated by Last Year's Capacity and Waiting List Impact
st.header("Section 2: Demand Treated by Last Year's Capacity and Waiting List Impact")

# Calculate treated demand based on last year's capacity
last_year_total_capacity = last_year_sessions * last_year_weeks * session_duration * last_year_utilization
st.write(f"**Total Capacity Last Year:** {last_year_total_capacity:.2f} hours")

# Input Waiting List Parameters
waiting_list_start = st.number_input('Waiting list at the start of next year', value=500)
waiting_time_target_weeks = st.number_input('Target weeks for waiting list cases', value=18)
over_target_percentage = st.slider('% of waiting list over target', 0.0, 1.0, 0.20)
breach_cases_percentage = st.slider('% of cases used to treat breaches', 0.0, 1.0, 0.30)

# Calculate End of Year Waiting List Size
treated_cases_for_breaches = last_year_total_capacity * breach_cases_percentage
treated_other_cases = last_year_total_capacity * (1 - breach_cases_percentage)
end_of_year_waiting_list = waiting_list_start - (treated_cases_for_breaches + treated_other_cases)
end_of_year_waiting_list = max(0, end_of_year_waiting_list)  # Avoid negative waiting list size
st.write(f"**Estimated Waiting List at End of Next Year:** {end_of_year_waiting_list}")

# Section 3 - Required Capacity to Meet Demand and Waiting Time Target
st.header("Section 3: Capacity Required to Meet Demand and Waiting Time Target")

# Allow users to adjust parameters
required_sessions = st.number_input('Required Sessions per Week', value=last_year_sessions)
required_utilization = st.slider('Required Utilization Percentage', min_value=0.0, max_value=1.0, value=last_year_utilization)

# Calculate required capacity
required_total_capacity = required_sessions * last_year_weeks * session_duration * required_utilization
required_to_meet_target = max(0, (waiting_list_start - end_of_year_waiting_list) / required_total_capacity)
st.write(f"**Required Capacity:** {required_total_capacity:.2f} hours")

# Plotly interactive chart for Total Demand per Procedure
st.subheader('Demand Hours per Procedure')
fig = px.bar(df, x='Procedure', y='Total Demand (Hours)', title='Total Demand per Procedure')
st.plotly_chart(fig)

# Plotly chart for Capacity and Demand Comparison
st.subheader('Capacity vs Demand')
capacity_vs_demand = pd.DataFrame({
    'Category': ['Total Demand', 'Total Capacity Last Year', 'Required Capacity'],
    'Hours': [total_demand_hours, last_year_total_capacity, required_total_capacity]
})
fig2 = px.bar(capacity_vs_demand, x='Category', y='Hours', title='Capacity vs Demand Comparison')
st.plotly_chart(fig2)

# Add a logo
st.sidebar.image('logo.jpeg', use_column_width=True)

# Export Results
st.sidebar.header('Export Results')
if st.sidebar.button('Download Results as CSV'):
    df_results = pd.DataFrame({
        'Total Demand Hours': [total_demand_hours],
        'Total Capacity Last Year (Hours)': [last_year_total_capacity],
        'Net Capacity (Hours)': [required_total_capacity],
        'End of Year Waiting List Size': [end_of_year_waiting_list]
    })
    df_results.to_csv('results.csv', index=False)
    st.sidebar.write('Results exported as `results.csv`')
