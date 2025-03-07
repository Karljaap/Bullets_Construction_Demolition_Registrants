import streamlit as st
import folium
import pandas as pd
from streamlit_folium import st_folium


# Cargar el archivo CSV de datos
def load_data(path):
    return pd.read_csv(path)


DATA_PATH = "filtered_data_march_clean.csv"
df = load_data(DATA_PATH)


# Crear un mapa con etiquetas que incluyan nombre, latitud y longitud
def create_map(data):
    mapa = folium.Map(location=[data['latitude'].mean(), data['longitude'].mean()], zoom_start=10,
                      tiles="OpenStreetMap")

    for _, row in data.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"<b>{row['account_name']}</b><br>Lat: {row['latitude']}, Lon: {row['longitude']}",
            tooltip=f"{row['account_name']} ({row['latitude']}, {row['longitude']})"
        ).add_to(mapa)

    return mapa


# Mostrar el mapa en Streamlit
st.title("Mapa con Etiquetas")
st_folium(create_map(df), width=700, height=500)