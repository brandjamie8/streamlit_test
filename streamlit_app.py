import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set the layout to wide
st.set_page_config(layout="wide")

# Section 1 - Data Upload and Manual Entry
st.title("Hospital Theatres Demand and Capacity App")
st.header("Section 1: Procedure Data and Last Year's Capacity")

# Initialize session state for procedures if not already present
if "procedures" not in st.session_state:
    st.session_state.procedures = [
        {"Procedure": "Procedure A", "Annual Demand (Cases)": 100, "Average Duration (Hours)": 2.0},
    ]

# Function to add new procedure to the list
def add_procedure():
    st.session_state.procedures.append(
        {
            "Procedure": st.session_state.procedure_name,
            "Annual Demand (Cases)": st.session_state.procedure_demand,
            "Average Duration (Hours)": st.session_state.procedure_duration,
        }
    )

# Section 1 - Data Upload and Manual Entry
st.title("Hospital Theatres Demand and Capacity App")
st.header("Section 1: Procedure Data Entry")

# Data Upload or Manual Entry
uploaded_file = st.file_uploader("Upload Procedure Data", type='csv')

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Uploaded data preview:")
    st.dataframe(df)
else:
    st.write("Manually enter procedure data")
    
    # Table-based data entry
    st.write("## Current Procedures")
    procedure_df = pd.DataFrame(st.session_state.procedures)
    st.dataframe(procedure_df)

    # Form to add a new procedure
    st.write("## Add a New Procedure")
    with st.form("procedure_form", clear_on_submit=True):
        procedure_name = st.text_input("Procedure Name", key="procedure_name")
        procedure_demand = st.number_input("Annual Demand (Cases)", key="procedure_demand", min_value=0, value=100)
        procedure_duration = st.number_input("Average Duration (Hours)", key="procedure_duration", min_value=0.0, value=1.0)
        submitted = st.form_submit_button("Add Procedure", on_click=add_procedure)

    # Convert session state into DataFrame for calculations
    df = pd.DataFrame(st.session_state.procedures)

# Calculate total demand
df['Total Demand (Minutes)'] = df['Annual Demand (Cases)'] * df['Average Duration (Hours)'] * 60
total_demand_minutes = df['Total Demand (Minutes)'].sum()

# Visualize total demand per procedure in cases and minutes
st.subheader('Total Demand by Procedure')

fig_demand_cases = px.bar(df, x='Procedure', y='Annual Demand (Cases)', title='Total Demand in Cases by Procedure')
st.plotly_chart(fig_demand_cases, use_container_width=True)

fig_demand_minutes = px.bar(df, x='Procedure', y='Total Demand (Minutes)', title='Total Demand in Minutes by Procedure')
st.plotly_chart(fig_demand_minutes, use_container_width=True)

# Display the total demand in minutes
st.write(f"**Total Demand (Minutes):** {total_demand_minutes}")

# Input Last Year's Capacity
st.subheader("Input Last Year's Capacity")
last_year_weeks = st.number_input('Weeks operating last year', value=48)
last_year_sessions = st.number_input('Sessions per week last year', value=10)
last_year_utilization = st.slider('Utilization Percentage', min_value=0.0, max_value=1.0, value=0.80, step=0.05)
session_duration = st.number_input('Session Duration (Hours)', value=4)

# Calculate last year's total capacity
last_year_total_sessions = last_year_weeks * last_year_sessions
last_year_total_minutes_per_session = session_duration * 60
last_year_total_capacity_minutes = last_year_total_sessions * last_year_total_minutes_per_session * last_year_utilization

st.write(f"**Last Year’s Total Sessions:** {last_year_total_sessions}")
st.write(f"**Session Minutes:** {last_year_total_minutes_per_session} minutes per session")
st.write(f"**Total Capacity Last Year:** {last_year_total_capacity_minutes:.2f} minutes")

# Section 2 - Demand Treated by Last Year's Capacity and Waiting List Impact
st.header("Section 2: Waiting List and Capacity Impact")

# Input Waiting List Parameters
waiting_list_start = st.number_input('Waiting list at the start of next year', value=500)
waiting_time_target_weeks = st.number_input('Target weeks for waiting list cases', value=18)
over_target_percentage = st.slider('% of waiting list over target', 0.0, 1.0, 0.20)
breach_cases_percentage = st.slider('% of cases used to treat breaches', 0.0, 1.0, 0.30)
waiting_list_addition = st.number_input('Number added to waiting list during the year', value=300)

# Calculate the numbers
treated_cases_for_breaches = last_year_total_capacity_minutes * breach_cases_percentage / (session_duration * 60)
treated_other_cases = last_year_total_capacity_minutes * (1 - breach_cases_percentage) / (session_duration * 60)
end_of_year_waiting_list = waiting_list_start + waiting_list_addition - (treated_cases_for_breaches + treated_other_cases)
backlog_end_of_year = waiting_list_start * over_target_percentage - treated_cases_for_breaches
backlog_end_of_year = max(0, backlog_end_of_year)

# Waterfall chart
st.subheader('Waterfall Chart: Waiting List Dynamics')

waterfall_fig = go.Figure(go.Waterfall(
    x=["Start of Year Waiting List", "New Additions", "Treated from Backlog", "Treated from Waiting List", "End of Year Waiting List"],
    y=[waiting_list_start, waiting_list_addition, -treated_cases_for_breaches, -treated_other_cases, end_of_year_waiting_list],
    measure=["absolute", "relative", "relative", "relative", "absolute"],
    text=[f"{waiting_list_start}", f"{waiting_list_addition}", f"{-treated_cases_for_breaches:.2f}", f"{-treated_other_cases:.2f}", f"{end_of_year_waiting_list:.2f}"],
    textposition="auto",
    connector={"line": {"color": "rgb(63, 63, 63)"}},
    decreasing={"marker": {"color": "red"}},
    increasing={"marker": {"color": "green"}},
    totals={"marker": {"color": "blue"}}
))

waterfall_fig.update_layout(title="Waiting List Dynamics Over the Year")
st.plotly_chart(waterfall_fig, use_container_width=True)

# Section 3 - Required Capacity
st.header("Section 3: Capacity Required to Meet Demand and Waiting Time Target")

required_sessions = st.number_input('Required Sessions per Week', value=last_year_sessions)
required_utilization = st.slider('Required Utilization Percentage', min_value=0.0, max_value=1.0, value=last_year_utilization)

# Calculate required capacity
required_total_sessions = required_sessions * last_year_weeks
required_total_capacity_minutes = required_total_sessions * last_year_total_minutes_per_session * required_utilization

st.write(f"**Required Capacity:** {required_total_capacity_minutes:.2f} minutes")

# Visualization: Required Capacity vs Demand
st.subheader('Required Capacity vs Demand')
capacity_vs_demand = pd.DataFrame({
    'Category': ['Total Demand (Minutes)', 'Last Year Capacity (Minutes)', 'Required Capacity (Minutes)'],
    'Minutes': [total_demand_minutes, last_year_total_capacity_minutes, required_total_capacity_minutes]
})
fig_capacity_vs_demand = px.bar(capacity_vs_demand, x='Category', y='Minutes', title='Required Capacity vs Demand Comparison')
st.plotly_chart(fig_capacity_vs_demand, use_container_width=True)

# Add a logo
st.sidebar.image('logo.jpg', use_column_width=True)

# Export Results
st.sidebar.header('Export Results')
if st.sidebar.button('Download Results as CSV'):
    df_results = pd.DataFrame({
        'Total Demand (Hours)': [total_demand_hours],
        'Total Demand (Minutes)': [total_demand_minutes],
        'Total Capacity Last Year (Minutes)': [last_year_total_capacity_minutes],
        'Net Capacity (Minutes)': [required_total_capacity_minutes],
        'End of Year Waiting List': [end_of_year_waiting_list],
        'End of Year Backlog': [backlog_end_of_year]
    })
    df_results.to_csv('results.csv', index=False)
    st.sidebar.write('Results exported as `results.csv`')



