import streamlit as st
import folium
import pandas as pd
from streamlit_folium import st_folium

# Load the CSV file
data_path = "filtered_data_march_clean.csv"
df = pd.read_csv(data_path)


# Create the map centered on the first location
def create_map(data):
    mapa = folium.Map(location=[data['latitude'].mean(), data['longitude'].mean()], zoom_start=12)

    for _, row in data.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"<b>Account:</b> {row['account_name']}",
            tooltip=row['account_name']
        ).add_to(mapa)

    return mapa


# Streamlit interface
st.title("Interactive Map Dashboard")
st.write("Visualization of data with geographic locations.")

# Display map
tabs = st.tabs(["Map", "Data"])

with tabs[0]:
    st.write("Location map:")
    mapa = create_map(df)
    st_folium(mapa, width=700, height=500)

with tabs[1]:
    st.write("Data table:")
    st.dataframe(df)