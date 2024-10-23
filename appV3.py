import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import random

# Set the layout to wide
st.set_page_config(
    #layout="wide",
    initial_sidebar_state="collapsed"

)

# Adjust the font size globally and add padding to the edges
st.markdown("""
    <style>
     body, p, div, span, h3, h4, h5, h6 {
        font-size: 18px; /* Set your desired font size */
    }
    .reportview-container .main .block-container{
        padding-left: 3rem;
        padding-right: 3rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar option to show or hide data labels
st.sidebar.header('Chart Options')
show_data_labels = st.sidebar.checkbox('Show Data Labels', value=True)

# ------------------------------ Section 1 – Procedure Demand ------------------------------

st.title("Admitted Demand and Capacity")
st.header("Section 1: Procedure Demand")

st.write("""
In this section, you can input your procedures along with their annual demand and average duration.
You can either upload a CSV file or manually input the data. 
""")

st.write("""
The app will calculate the total demand in cases and minutes, and display the top 10 procedures in terms of demand.
""")

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

# Data Upload or Manual Entry
uploaded_file = st.file_uploader("Upload Procedure Data", type='csv')

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Uploaded data preview:")
    st.dataframe(df)
else:
    st.write("Or manually enter procedure data:")
    
    # Table-based data entry
    st.write("##Procedures Added to the Admitted Waiting List (Yearly):")
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
total_demand_cases = df['Annual Demand (Cases)'].sum()
total_demand_minutes = df['Total Demand (Minutes)'].sum()

st.write(f"**Total Demand (Cases):** {total_demand_cases:.0f}")
st.write(f"**Total Demand (Minutes):** {total_demand_minutes:.0f}")

# Sort and select top 10 procedures by demand in cases
top10_cases = df.sort_values(by='Annual Demand (Cases)', ascending=False).head(10)

# Chart - Top 10 procedure demand in cases
fig_top10_cases = px.bar(
    top10_cases,
    x='Procedure',
    y='Annual Demand (Cases)',
    title='Top 10 Procedures by Demand in Cases',
    text='Annual Demand (Cases)' if show_data_labels else None
)
st.plotly_chart(fig_top10_cases, use_container_width=True)

# Sort and select top 10 procedures by demand in minutes
top10_minutes = df.sort_values(by='Total Demand (Minutes)', ascending=False).head(10)

# Chart - Top 10 procedure demand in session minutes
fig_top10_minutes = px.bar(
    top10_minutes,
    x='Procedure',
    y='Annual Demand (Minutes)',
    title='Top 10 Procedures by Demand in Session Minutes',
    text='Total Demand (Minutes)' if show_data_labels else None
)
st.plotly_chart(fig_top10_minutes, use_container_width=True)

# Add multiplier variable for next year's demand
st.write("## Next Year's Demand Adjustment")
st.write("If demand is expected to increase for next year add a multiplier here:")
multiplier = st.number_input("Multiplier for Next Year's Demand", min_value=0.0, value=1.0, step=0.1)

# Calculate next year's demand
df['Next Year Demand (Cases)'] = df['Annual Demand (Cases)'] * multiplier
df['Next Year Demand (Minutes)'] = df['Next Year Demand (Cases)'] * df['Average Duration (Hours)'] * 60

next_year_total_demand_cases = df['Next Year Demand (Cases)'].sum()
next_year_total_demand_minutes = df['Next Year Demand (Minutes)'].sum()

st.write(f"**Next Year's Total Demand (Cases):** {next_year_total_demand_cases:.0f}")
st.write(f"**Next Year's Total Demand (Minutes):** {next_year_total_demand_minutes:.0f}")

# ------------------------------ Section 2 – Sessions Last Year ------------------------------

st.header("Section 2: Sessions Last Year")

st.write("""
In this section, you can input the variables related to last year's sessions, such as weeks per year,
sessions per week, and utilisation percentage. The app will calculate the total sessions and session minutes
for last year and compare it with the total demand minutes.
""")

# Input variables for last year
st.write("## Input Last Year's Variables")

weeks_last_year = st.number_input("Weeks per Year (Last Year)", min_value=1, max_value=52, value=48)
sessions_per_week_last_year = st.number_input("Sessions per Week (Last Year)", min_value=0.0, value=10.0, step=0.1)
utilisation_last_year = st.slider("Utilisation Percentage (Last Year)", min_value=0.0, max_value=1.0, value=0.80, step=0.01)
session_duration_hours = st.number_input("Session Duration (Hours)", min_value=0.0, value=4.0, step=0.5)

# Calculate total sessions and session minutes last year
total_sessions_last_year = weeks_last_year * sessions_per_week_last_year
session_minutes_last_year = total_sessions_last_year * session_duration_hours * 60 * utilisation_last_year

st.write(f"**Total Sessions Last Year:** {total_sessions_last_year:.2f}")
st.write(f"**Total Session Minutes Last Year (after Utilisation):** {session_minutes_last_year:.0f}")

# Chart – Total demand minutes last year vs total session minutes last year
demand_vs_capacity_last_year = pd.DataFrame({
    'Category': ['Total Demand Minutes Last Year', 'Total Session Minutes Last Year'],
    'Minutes': [total_demand_minutes, session_minutes_last_year]
})

fig_demand_vs_capacity_last_year = px.bar(
    demand_vs_capacity_last_year,
    x='Category',
    y='Minutes',
    title='Total Demand Minutes vs Total Session Minutes Last Year',
    text='Minutes' if show_data_labels else None
)
st.plotly_chart(fig_demand_vs_capacity_last_year, use_container_width=True)

# ------------------------------ Section 3 – Demand vs Capacity ------------------------------

st.header("Section 3: Demand vs Capacity")

st.write("""
In this section, we'll compare the demand with the capacity by performing random sampling from last year's
demand to fill last year's available capacity. We'll also calculate the expected cases treated and compare
with the actual cases treated (if provided). You can choose to use the same capacity as last year or input
a new capacity model for next year.
""")

# Input number of cases last year actually treated for comparison
actual_cases_treated_last_year = st.number_input("Number of Cases Actually Treated Last Year (Optional)", min_value=0, value=0)

# Choose capacity model for next year
st.write("## Capacity Model Selection")

capacity_model = st.radio(
    "Choose Capacity Model for Next Year",
    ('Same as Last Year', 'New Capacity Model')
)

if capacity_model == 'New Capacity Model':
    st.write("## Input Next Year's Variables")

    weeks_next_year = st.number_input("Weeks per Year (Next Year)", min_value=1, max_value=52, value=48)
    sessions_per_week_next_year = st.number_input(
        "Sessions per Week (Next Year)",
        min_value=0.0,
        value=10.0,
        step=0.1
    )
    utilisation_next_year = st.slider("Utilisation Percentage (Next Year)", min_value=0.0, max_value=1.0, value=0.80, step=0.01)
else:
    weeks_next_year = weeks_last_year
    sessions_per_week_next_year = sessions_per_week_last_year
    utilisation_next_year = utilisation_last_year

# Calculate total sessions and session minutes next year
total_sessions_next_year = weeks_next_year * sessions_per_week_next_year
session_minutes_next_year = total_sessions_next_year * session_duration_hours * 60 * utilisation_next_year

st.write(f"**Total Sessions Next Year:** {total_sessions_next_year:.2f}")
st.write(f"**Total Session Minutes Next Year (after Utilisation):** {session_minutes_next_year:.0f}")

# Function to simulate cases treated based on capacity
def simulate_cases_treated(demand_df, total_capacity_minutes):
    # Create a list of procedures proportional to their demand
    case_list = []
    for idx, row in demand_df.iterrows():
        num_cases = int(row['Next Year Demand (Cases)'])
        case_list.extend([row['Procedure']] * num_cases)
    # Shuffle the list
    random.shuffle(case_list)
    # Now accumulate durations until capacity is reached
    cases_treated = []
    total_minutes = 0
    for procedure in case_list:
        duration_minutes = demand_df.loc[demand_df['Procedure'] == procedure, 'Average Duration (Hours)'].values[0] * 60
        if total_minutes + duration_minutes <= total_capacity_minutes:
            total_minutes += duration_minutes
            cases_treated.append({'Procedure': procedure, 'Duration (Minutes)': duration_minutes})
        else:
            break
    # Convert to DataFrame
    cases_treated_df = pd.DataFrame(cases_treated)
    return cases_treated_df, total_minutes

# Simulate cases treated last year
cases_treated_last_year_df, total_minutes_treated_last_year = simulate_cases_treated(
    df.assign(**{'Next Year Demand (Cases)': df['Annual Demand (Cases)']}), session_minutes_last_year
)

expected_cases_treated_last_year = len(cases_treated_last_year_df)
st.write(f"**Expected Cases Treated Last Year (Simulated):** {expected_cases_treated_last_year:.0f}")
st.write(f"**Total Minutes Treated Last Year (Simulated):** {total_minutes_treated_last_year:.0f}")

# Simulate cases treated next year
cases_treated_next_year_df, total_minutes_treated_next_year = simulate_cases_treated(df, session_minutes_next_year)

expected_cases_treated_next_year = len(cases_treated_next_year_df)
st.write(f"**Expected Cases Treated Next Year (Simulated):** {expected_cases_treated_next_year:.0f}")
st.write(f"**Total Minutes Treated Next Year (Simulated):** {total_minutes_treated_next_year:.0f}")

# Chart - Expected cases last year vs actual cases last year (if input) vs expected cases next year
cases_comparison_df = pd.DataFrame({
    'Category': ['Expected Cases Last Year (Simulated)', 'Actual Cases Last Year', 'Expected Cases Next Year (Simulated)'],
    'Cases': [expected_cases_treated_last_year, actual_cases_treated_last_year, expected_cases_treated_next_year]
})

# Exclude 'Actual Cases Last Year' if not provided
if actual_cases_treated_last_year == 0:
    cases_comparison_df = cases_comparison_df[cases_comparison_df['Category'] != 'Actual Cases Last Year']

fig_cases_comparison = px.bar(
    cases_comparison_df,
    x='Category',
    y='Cases',
    title='Expected vs Actual Cases Treated',
    text='Cases' if show_data_labels else None
)
st.plotly_chart(fig_cases_comparison, use_container_width=True)

# Given weeks next year and utilisation %, how many sessions required to get enough minutes for next year’s demand?
required_capacity_minutes_next_year = next_year_total_demand_minutes

required_total_sessions_next_year = required_capacity_minutes_next_year / (session_duration_hours * 60 * utilisation_next_year)
required_sessions_per_week_next_year = required_total_sessions_next_year / weeks_next_year

st.write(f"**Required Sessions per Week to Meet Next Year's Demand:** {required_sessions_per_week_next_year:.2f}")

# Chart – expected sessions next year vs required sessions next year
sessions_comparison_df = pd.DataFrame({
    'Category': ['Expected Sessions per Week Next Year', 'Required Sessions per Week Next Year'],
    'Sessions per Week': [sessions_per_week_next_year, required_sessions_per_week_next_year]
})

fig_sessions_comparison = px.bar(
    sessions_comparison_df,
    x='Category',
    y='Sessions per Week',
    title='Expected vs Required Sessions per Week Next Year',
    text='Sessions per Week' if show_data_labels else None
)
st.plotly_chart(fig_sessions_comparison, use_container_width=True)

# Calculate percentage difference in sessions per week
sessions_difference_percentage = ((sessions_per_week_next_year - required_sessions_per_week_next_year) / required_sessions_per_week_next_year) * 100
sessions_difference_percentage = round(sessions_difference_percentage, 2)

# Determine if there is enough capacity planned
if sessions_per_week_next_year >= required_sessions_per_week_next_year:
    assessment = "There is **enough capacity** planned to meet the demand."
else:
    assessment = "There is **not enough capacity** planned to meet the demand."

st.write(f"**Percentage Difference in Sessions per Week:** {sessions_difference_percentage}%")
st.write(f"**Assessment:** {assessment}")

# Compare number of cases
cases_difference_percentage = ((expected_cases_treated_next_year - next_year_total_demand_cases) / next_year_total_demand_cases) * 100
cases_difference_percentage = round(cases_difference_percentage, 2)

st.write(f"**Next Year's Demand (Cases):** {next_year_total_demand_cases:.0f}")
st.write(f"**Expected Cases Treated Next Year (Capacity):** {expected_cases_treated_next_year:.0f}")
st.write(f"**Percentage Difference in Cases:** {cases_difference_percentage}%")

# ------------------------------ Section 4 – Waiting List ------------------------------

st.header("Section 4: Waiting List")

st.write("""
In this section, you can analyze the waiting list dynamics for either last year or next year.
""")

# Select year for waiting list analysis
year_selection = st.radio(
    "Select Year for Waiting List Analysis",
    ('Last Year', 'Next Year')
)

# Input waiting list variables
st.write("## Input Waiting List Variables")

waiting_list_start = st.number_input('Waiting List at the Start of the Year', min_value=0, value=500)
waiting_list_target_weeks = st.number_input('Waiting List Target (Weeks Wait)', min_value=0, value=18)
waiting_list_breaching_percentage = st.slider('% of Waiting List Breaching Target', min_value=0.0, max_value=1.0, value=0.20, step=0.01)

# Set default waiting list addition based on the selected year
if year_selection == 'Next Year':
    default_waiting_list_addition = next_year_total_demand_cases
else:
    default_waiting_list_addition = total_demand_cases

waiting_list_addition = st.number_input(
    'Number Added to Waiting List During the Year',
    min_value=0,
    value=int(default_waiting_list_addition)
)

# Calculate breaches
breaches_start = waiting_list_start * waiting_list_breaching_percentage
non_breaches_start = waiting_list_start - breaches_start + waiting_list_addition

# Choose capacity for waiting list analysis
st.write("## Select Capacity to Use")

capacity_option = st.radio(
    "Choose Capacity for Waiting List Analysis",
    ('Last Year Capacity', 'Next Year Expected Capacity', 'Next Year Required Capacity')
)

if capacity_option == 'Last Year Capacity':
    total_capacity_minutes = session_minutes_last_year
elif capacity_option == 'Next Year Expected Capacity':
    total_capacity_minutes = session_minutes_next_year
else:
    total_capacity_minutes = required_capacity_minutes_next_year

# Demand for the selected year
if year_selection == 'Next Year':
    demand_cases = next_year_total_demand_cases
    demand_df = df.copy()
else:
    demand_cases = total_demand_cases
    demand_df = df.assign(**{'Next Year Demand (Cases)': df['Annual Demand (Cases)']})

# Variable - % Of cases used to treat breaches
breach_cases_percentage = st.slider('% of Cases Used to Treat Breaches', min_value=0.0, max_value=1.0, value=0.30, step=0.01)

# Average duration in minutes
average_duration_minutes = (demand_df['Average Duration (Hours)'] * 60).mean()

# Capacity minutes allocated
capacity_minutes_for_breaches = total_capacity_minutes * breach_cases_percentage
capacity_minutes_for_non_breaches = total_capacity_minutes * (1 - breach_cases_percentage)

# Expected breaches treated
expected_breaches_treated = min(breaches_start, capacity_minutes_for_breaches / average_duration_minutes)
breaches_end = breaches_start - expected_breaches_treated

# Expected non-breaches treated
expected_non_breaches_treated = min(non_breaches_start, capacity_minutes_for_non_breaches / average_duration_minutes)
non_breaches_end = non_breaches_start - expected_non_breaches_treated

# Total waiting list at the end of the year
waiting_list_end = breaches_end + non_breaches_end

st.write(f"**Breaches at Start of Year:** {breaches_start:.0f}")
st.write(f"**Expected Breaches Treated:** {expected_breaches_treated:.0f}")
st.write(f"**Breaches at End of Year:** {breaches_end:.0f}")

st.write(f"**Non-Breaches at Start of Year (including additions):** {non_breaches_start:.0f}")
st.write(f"**Expected Non-Breaches Treated:** {expected_non_breaches_treated:.0f}")
st.write(f"**Non-Breaches at End of Year:** {non_breaches_end:.0f}")

st.write(f"**Total Waiting List at End of Year:** {waiting_list_end:.0f}")

# Waterfall chart for waiting list dynamics
st.subheader('Waterfall Chart: Waiting List Dynamics')

measure = ["absolute", "relative", "relative", "relative", "total"]

x = ["Start of Year Waiting List", "Additions", "Breaches Treated", "Non-Breaches Treated", "End of Year Waiting List"]
y = [waiting_list_start, waiting_list_addition, -expected_breaches_treated, -expected_non_breaches_treated, waiting_list_end]

text = [f"{val:.0f}" for val in y] if show_data_labels else None

waterfall_fig = go.Figure(go.Waterfall(
    name = "Waiting List",
    orientation = "v",
    measure = measure,
    x = x,
    y = y,
    textposition = "outside",
    text = text,
    connector = {"line":{"color":"rgb(63, 63, 63)"}},
    decreasing={"marker":{"color":"green"}},
    increasing={"marker":{"color":"red"}},
    totals={"marker":{"color":"blue"}}
))

waterfall_fig.update_layout(
    title = "Waiting List Dynamics Over the Year",
    showlegend = False
)

st.plotly_chart(waterfall_fig, use_container_width=True)

# ------------------------------ Section 5 – Results ------------------------------

st.header("Section 5: Results")

st.write("""
This section summarizes the key results from the previous sections.
""")

# Expected cases next year – demand and capacity
st.write(f"**Expected Cases Next Year (Demand):** {next_year_total_demand_cases:.0f}")
st.write(f"**Expected Cases Treated Next Year (Capacity):** {expected_cases_treated_next_year:.0f}")

# Expected minutes next year – demand and capacity
st.write(f"**Expected Minutes Next Year (Demand):** {next_year_total_demand_minutes:.0f}")
st.write(f"**Expected Minutes Treated Next Year (Capacity):** {total_minutes_treated_next_year:.0f}")

# Expected change in waiting list next year – start and finish (and backlog)
st.write(f"**Waiting List at Start of Year:** {waiting_list_start:.0f}")
st.write(f"**Waiting List at End of Year:** {waiting_list_end:.0f}")
st.write(f"**Change in Waiting List:** {(waiting_list_end - waiting_list_start):.0f}")

# Sessions required per week to meet demand completely
st.write(f"**Sessions Required per Week to Meet Next Year's Demand Completely:** {required_sessions_per_week_next_year:.2f}")

# Difference between sessions required, sessions last year and sessions planned for next year
difference_sessions = required_sessions_per_week_next_year - sessions_per_week_next_year
st.write(f"**Difference between Required and Planned Sessions per Week Next Year:** {difference_sessions:.2f}")
