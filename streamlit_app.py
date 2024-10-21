import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Section 1 - Data Entry for Procedures (Manual or Upload)
st.title("Hospital Theatres Demand and Capacity App")
st.header("Procedure Data and Capacity Calculation")

# Placeholder for Procedure Data
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

# Input Last Year Capacity Parameters
st.subheader("Input Last Year's Capacity")
last_year_weeks = st.number_input('Weeks operating last year', value=48)
last_year_sessions = st.number_input('Sessions per week last year', value=10)
session_duration = st.number_input('Session Duration (Hours)', value=4)
utilization_percentage = st.slider('Utilization Percentage', min_value=0.0, max_value=1.0, value=0.80, step=0.05)

# Calculate last year's capacity
total_capacity_minutes = last_year_weeks * last_year_sessions * session_duration * 60 * utilization_percentage

# Waiting List Parameters
st.header("Waiting List and Backlog Management")
waiting_list_start = st.number_input('Start of Year Waiting List', value=500)
backlog_percentage_start = st.slider('% of Waiting List Backlog (Over Time Target)', min_value=0.0, max_value=1.0, value=0.20)
waiting_list_additions = st.number_input('New Additions to Waiting List During the Year', value=300)

# Backlog and Non-Backlog Breakdown
backlog_start = waiting_list_start * backlog_percentage_start
non_backlog_start = waiting_list_start - backlog_start

# Treated Cases Breakdown
backlog_treated_percentage = st.slider('% of Capacity Used to Treat Backlog', min_value=0.0, max_value=1.0, value=0.30)
backlog_treated = total_capacity_minutes * backlog_treated_percentage / (session_duration * 60)
non_backlog_treated = total_capacity_minutes * (1 - backlog_treated_percentage) / (session_duration * 60)

# Calculate End of Year Waiting List and Backlog
backlog_end = max(0, backlog_start - backlog_treated)
non_backlog_end = max(0, (waiting_list_start - backlog_start + waiting_list_additions) - non_backlog_treated)
waiting_list_end = backlog_end + non_backlog_end

# Waterfall Chart for Backlog and Waiting List Management
st.subheader('Waterfall Chart: Waiting List Dynamics')

waterfall_fig = go.Figure(go.Waterfall(
    x=["Start of Year: Backlog", "Start of Year: Waiting List", "New Additions", "Treated: Backlog", "Treated: Waiting List", "End of Year: Backlog", "End of Year: Waiting List"],
    y=[backlog_start, non_backlog_start, waiting_list_additions, -backlog_treated, -non_backlog_treated, backlog_end, non_backlog_end],
    measure=["absolute", "absolute", "relative", "relative", "relative", "absolute", "absolute"],
    text=[f"{backlog_start:.2f}", f"{non_backlog_start:.2f}", f"{waiting_list_additions:.2f}", f"{-backlog_treated:.2f}", f"{-non_backlog_treated:.2f}", f"{backlog_end:.2f}", f"{non_backlog_end:.2f}"],
    textposition="auto",
    connector={"line": {"color": "rgb(63, 63, 63)"}},
    decreasing={"marker": {"color": "red"}},
    increasing={"marker": {"color": "green"}},
    totals={"marker": {"color": "blue"}}
))

waterfall_fig.update_layout(title="Waiting List Dynamics Over the Year")
st.plotly_chart(waterfall_fig, use_container_width=True)

# Display Results
st.write(f"**Total Capacity (Minutes):** {total_capacity_minutes:.2f}")
st.write(f"**Backlog at End of Year:** {backlog_end:.2f}")
st.write(f"**Non-Backlog at End of Year:** {non_backlog_end:.2f}")
st.write(f"**Total Waiting List at End of Year:** {waiting_list_end:.2f}")

