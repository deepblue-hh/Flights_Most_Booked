import streamlit as st
import pandas as pd
import plotly.express as px

# Define the colors
colors = px.colors.qualitative.Plotly

# Load the data
@st.cache_data
def load_data():
    df = pd.read_csv('./data/amadeus_test_production_aug.csv')
    iata_codes = pd.read_csv('./data/IATA_city_code.csv')
    return df, iata_codes

df, iata_codes = load_data()

# Replace the origin and destination codes with city and country names
df = df.merge(iata_codes, left_on='origin', right_on='都市コード', how='left')
df.rename(columns={'都市名': 'origin_city', '国名': 'origin_country'}, inplace=True)
df.drop(columns='都市コード', inplace=True)

df = df.merge(iata_codes, left_on='destination', right_on='都市コード', how='left')
df.rename(columns={'都市名': 'destination_city', '国名': 'destination_country'}, inplace=True)
df.drop(columns='都市コード', inplace=True)

# Reordering columns to control hover_data order
df = df[['month', 'destination_city', 'destination_country', 'origin_city', 'origin_country', 'score_flights', 'score_travelers']]

# Convert 'month' column to datetime format
df['month'] = pd.to_datetime(df['month'])

# Add title
st.title('Amadeus Flights Most Booked Dashboard')

# Add a radio button to the sidebar for origin:
selected_origin = st.sidebar.radio(
    'Select origin',
    df['origin_city'].unique()
)

# Add a radio button to the sidebar for score type:
selected_score = st.sidebar.radio(
    'Select score type',
    ['score_flights', 'score_travelers']
)

# Filtering data based on the selected origin
filtered_data = df[df['origin_city'] == selected_origin]

# Group by 'month' and 'destination', and calculate mean scores
grouped_data = filtered_data.groupby(['month', 'destination_city', 'destination_country'])[selected_score].mean().reset_index()

# Add a number input to the sidebar for the top destinations:
top_destinations = st.sidebar.number_input('Select top destinations', min_value=1, max_value=30, value=10)

# Sort by score and take the top destinations across all months
top_data = grouped_data.groupby(['destination_city', 'destination_country'])[selected_score].mean().nlargest(top_destinations).reset_index()

# Filtering data based on the top destinations
final_data = grouped_data[grouped_data['destination_city'].isin(top_data['destination_city'])]

# Create an ordered category based on the scores in the most recent month
ordered_destinations = top_data['destination_city']
final_data['destination_city'] = pd.Categorical(final_data['destination_city'], categories=ordered_destinations, ordered=True)

# Create a color mapping
color_mapping = {city: colors[i % len(colors)] for i, city in enumerate(ordered_destinations)}

# Plotting with Plotly
fig = px.line(final_data, x='month', y=selected_score, color='destination_city', color_discrete_map=color_mapping, hover_data={'destination_city': True, 'destination_country': True, 'month': True, selected_score: True})
st.plotly_chart(fig)
