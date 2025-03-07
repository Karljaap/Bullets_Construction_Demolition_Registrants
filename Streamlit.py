import streamlit as st
import folium
import pandas as pd
from streamlit_folium import st_folium

# Cargar el archivo CSV de datos
def load_data(path):
    return pd.read_csv(path)

DATA_PATH = "filtered_data_march_clean.csv"
df = load_data(DATA_PATH)

# Crear un mapa simple con tiles válidos
def create_map(data):
    mapa = folium.Map(location=[data['latitude'].mean(), data['longitude'].mean()], zoom_start=10, tiles="OpenStreetMap")
    return mapa

# Mostrar el mapa en Streamlit
st.title("Mapa Simple")
st_folium(create_map(df), width=700, height=500)