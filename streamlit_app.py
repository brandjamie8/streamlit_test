# streamlit_app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Sidebar - Upload File
st.sidebar.header('Upload Procedure Data')
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type='csv')

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    st.sidebar.write('Using default procedure data.')
    # Default Data
    procedures = ['Procedure A', 'Procedure B', 'Procedure C']
    annual_demand_cases = [100, 150, 200]
    average_durations = [2.0, 1.5, 1.0]
    df = pd.DataFrame({
        'Procedure': procedures,
        'Annual Demand (Cases)': annual_demand_cases,
        'Average Duration (Hours)': average_durations
    })

# Calculate Total Demand Hours
df['Total Demand (Hours)'] = df['Annual Demand (Cases)'] * df['Average Duration (Hours)']
total_demand_hours = df['Total Demand (Hours)'].sum()

st.title('Theatres Demand and Capacity')

st.sidebar.header('Theatre Parameters')
sessions_per_week = st.sidebar.slider('Sessions per Week', min_value=0, max_value=20, value=10)
weeks_operating_per_year = st.sidebar.slider('Weeks Operating per Year', min_value=0, max_value=52, value=48)
utilization_percentage = st.sidebar.slider('Utilisation Percentage', min_value=0.0, max_value=1.0, value=0.80, step=0.05)
session_duration = st.sidebar.number_input('Session Duration (Hours)', value=4)

total_capacity_hours = sessions_per_week * weeks_operating_per_year * session_duration * utilization_percentage
net_capacity_hours = total_capacity_hours - total_demand_hours
percentage_demand_met = (total_capacity_hours / total_demand_hours) * 100 if total_demand_hours > 0 else 0

st.subheader('Results')
st.write(f"**Total Demand Hours:** {total_demand_hours}")
st.write(f"**Total Capacity Hours:** {total_capacity_hours:.2f}")
st.write(f"**Net Capacity (Hours):** {net_capacity_hours:.2f}")
st.write(f"**Percentage of Demand Met:** {percentage_demand_met:.2f}%")

labels = ['Total Demand', 'Total Capacity']
values = [total_demand_hours, total_capacity_hours]
colors = ['#1f77b4', '#ff7f0e']

fig, ax = plt.subplots()
ax.bar(labels, values, color=colors)
ax.set_ylabel('Hours')
ax.set_title('Demand vs Capacity')
st.pyplot(fig)

st.subheader('Demand Hours per Procedure')
fig2, ax2 = plt.subplots()
df.plot(kind='bar', x='Procedure', y='Total Demand (Hours)', ax=ax2, color='purple')
ax2.set_ylabel('Total Demand (Hours)')
st.pyplot(fig2)

st.subheader('Procedure Details')
st.dataframe(df)

st.sidebar.header('Export Results')
if st.sidebar.button('Download Results as CSV'):
    df_results = pd.DataFrame({
        'Total Demand Hours': [total_demand_hours],
        'Total Capacity Hours': [total_capacity_hours],
        'Net Capacity (Hours)': [net_capacity_hours],
        'Percentage of Demand Met': [percentage_demand_met]
    })
    df_results.to_csv('results.csv', index=False)
    st.sidebar.write('Results exported as `results.csv`')
