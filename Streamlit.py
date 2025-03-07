import os
import streamlit as st
import folium
import pandas as pd
import requests
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from concurrent.futures import ThreadPoolExecutor
from io import StringIO

# Base parameters
BASE_URL = "https://data.cityofnewyork.us/resource/cspg-yi7g.csv?$query="
QUERY_TEMPLATE = "SELECT created, account_name, latitude, longitude WHERE created >= '{start_date}' AND created <= '{end_date}' ORDER BY created DESC NULL FIRST"
LIMIT = 5000  # Number of records per request


# Function to fetch data with pagination and date filtering
def fetch_data(offset, start_date, end_date):
    query = QUERY_TEMPLATE.format(start_date=start_date, end_date=end_date)
    url = f"{BASE_URL}{query} LIMIT {LIMIT} OFFSET {offset}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text))
        return df if not df.empty else None
    except Exception as e:
        print(f"Error fetching data at offset {offset}: {e}")
        return None


# Main function to retrieve and consolidate the data
def get_filtered_data(start_date, end_date):
    print(f"Fetching data from {start_date} to {end_date}...")

    # Fetch the first batch to verify if there is data available
    initial_df = fetch_data(0, start_date, end_date)
    if initial_df is None:
        print("No data found within the specified date range.")
        return None

    # List to store results
    all_data = [initial_df]
    total_records = len(initial_df)

    print(f"First batch retrieved: {total_records} records.")

    # Create a list of offsets for pagination
    offsets = list(range(LIMIT, 1000000, LIMIT))  # Up to 1 million records

    # Fetch data in parallel
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(lambda offset: fetch_data(offset, start_date, end_date), offsets))

    # Add only the results that contain data
    for result in results:
        if result is not None:
            all_data.append(result)

    # Combine all data into a single DataFrame
    data = pd.concat(all_data, ignore_index=True)
    print(f"Total records retrieved: {len(data)}")

    return data


# Streamlit app title
st.title("NYC Incident Report Map")

# Date range selection
start_date = st.date_input("Start Date", value=pd.to_datetime("2025-02-01"))
end_date = st.date_input("End Date", value=pd.to_datetime("2025-03-06"))

# Fetch data button
if st.button("Fetch Data"):
    filtered_data = get_filtered_data(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

    if filtered_data is not None:
        # Convert 'created' column to datetime format
        filtered_data['created'] = pd.to_datetime(filtered_data['created'])

        # Clean NaN values in latitude and longitude
        filtered_data_clean = filtered_data.dropna(subset=['latitude', 'longitude'])

        # Create a Folium map centered on an average location of the data
        if not filtered_data_clean.empty:
            map_center = [filtered_data_clean['latitude'].mean(), filtered_data_clean['longitude'].mean()]
            mymap = folium.Map(location=map_center, zoom_start=12)

            # Add markers
            marker_cluster = MarkerCluster().add_to(mymap)
            for _, row in filtered_data_clean.iterrows():
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=row['account_name'],
                    tooltip=row['account_name']
                ).add_to(marker_cluster)

            # Display the map
            st_folium(mymap, width=700, height=500)

            # Display the filtered dataset
            st.subheader("Filtered Data Table")
            st.dataframe(filtered_data_clean[['created', 'account_name', 'latitude', 'longitude']])
        else:
            st.write("No data found for the selected date range.")
