import streamlit as st
import folium
import pandas as pd
from streamlit_folium import st_folium

# Cargar el archivo CSV de datos
def load_data(path):
    return pd.read_csv(path)

DATA_PATH = "filtered_data_march_clean.csv"
df = load_data(DATA_PATH)

# Crear el mapa
def create_map(data):
    mapa = folium.Map(location=[data['latitude'].mean(), data['longitude'].mean()], zoom_start=12, tiles="OpenStreetMap")
    for _, row in data.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=row['account_name'],
            tooltip=row['account_name']
        ).add_to(mapa)
    return mapa

# Mostrar el mapa en Streamlit
st.title("Mapa Interactivo")
st_folium(create_map(df), width=700, height=500)
