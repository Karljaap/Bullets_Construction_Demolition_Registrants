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

try:
    df = pd.read_csv(DATA_PATH)
except Exception as e:
    st.error(f"Error al cargar el archivo CSV: {e}")
    st.stop()

# Verificar que el CSV contenga las columnas necesarias
required_columns = ['latitude', 'longitude', 'account_name']
for col in required_columns:
    if col not in df.columns:
        st.error(f"Falta la columna requerida: {col}")
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

# Mostrar el mapa y los datos en pestañas
tabs = st.tabs(["Mapa", "Datos"])

with tabs[0]:
    st.write("Mapa de Ubicaciones:")
    mapa = create_map(df)
    st_folium(mapa, width=700, height=500)

with tabs[1]:
    st.write("Tabla de Datos:")
    st.dataframe(df)