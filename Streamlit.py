import os
import streamlit as st
import folium
import pandas as pd
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

# Cargar el archivo CSV de datos
DATA_PATH = "filtered_data_march_clean.csv"

if not os.path.exists(DATA_PATH):
    st.error("Error: No se encontró el archivo de datos. Verifique la ruta.")
    st.stop()


# Cargar datos con manejo de errores
@st.cache_data
def load_data(path):
    try:
        df = pd.read_csv(path)
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo CSV: {e}")
        st.stop()


# Cargar los datos con caché
df = load_data(DATA_PATH)

# Verificar que el CSV contenga las columnas necesarias
required_columns = ['latitude', 'longitude', 'account_name']
if not all(col in df.columns for col in required_columns):
    st.error("Faltan columnas requeridas en el archivo CSV")
    st.stop()


# Crear el mapa con clusters para mejorar la visualización
def create_map(data):
    mapa = folium.Map(location=[data['latitude'].mean(), data['longitude'].mean()], zoom_start=12,
                      tiles="OpenStreetMap")
    cluster = MarkerCluster().add_to(mapa)

    for _, row in data.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"<b>Account:</b> {row['account_name']}",
            tooltip=row['account_name']
        ).add_to(cluster)

    return mapa


# Interfaz en Streamlit
st.title("Interactive Map Dashboard")
st.write("Visualización de datos con ubicaciones geográficas.")

# Mostrar solo el mapa interactivo
mapa = create_map(df)
st_folium(mapa, width=700, height=500)
