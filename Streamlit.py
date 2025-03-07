import os
import streamlit as st
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor
from io import StringIO

# Configuración de la página
st.set_page_config(page_title="NYC Incident Report Data", layout="wide")

# Base parameters
BASE_URL = "https://data.cityofnewyork.us/resource/cspg-yi7g.csv?$query="
QUERY_TEMPLATE = "SELECT created, account_name, latitude, longitude WHERE created >= '{start_date}' AND created <= '{end_date}' ORDER BY created DESC NULL FIRST"
LIMIT = 5000  # Número de registros por solicitud

# Función para obtener datos con paginación y filtrado por fecha
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

# Función principal para recuperar y consolidar los datos
def get_filtered_data(start_date, end_date):
    print(f"Fetching data from {start_date} to {end_date}...")
    initial_df = fetch_data(0, start_date, end_date)
    if initial_df is None:
        print("No data found within the specified date range.")
        return None

    all_data = [initial_df]
    offsets = list(range(LIMIT, 1000000, LIMIT))
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(lambda offset: fetch_data(offset, start_date, end_date), offsets))
    for result in results:
        if result is not None:
            all_data.append(result)
    data = pd.concat(all_data, ignore_index=True)
    print(f"Total records retrieved: {len(data)}")
    return data

# Pestañas
tab1, tab2, tab3, tab4 = st.tabs(["Data Retrieval", "Filtered Data", "Analysis", "References"])

with tab1:
    st.markdown("""
    ## Data Retrieval
    Select a date range to fetch incident reports from the NYC database.
    """)
    start_date = st.date_input("Start Date", value=pd.to_datetime("2025-02-01"))
    end_date = st.date_input("End Date", value=pd.to_datetime("2025-03-06"))
    if st.button("Fetch Data"):
        filtered_data = get_filtered_data(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        st.session_state["filtered_data"] = filtered_data

with tab2:
    st.markdown("""
    ## Filtered Data
    View the retrieved incident reports.
    """)
    if "filtered_data" in st.session_state and st.session_state["filtered_data"] is not None:
        filtered_data = st.session_state["filtered_data"]
        filtered_data['created'] = pd.to_datetime(filtered_data['created'])
        filtered_data_clean = filtered_data.dropna(subset=['latitude', 'longitude'])
        st.dataframe(filtered_data_clean[['created', 'account_name', 'latitude', 'longitude']])
    else:
        st.write("No data found for the selected date range.")

with tab3:
    st.markdown("""
    ## Analysis
    This section can include further analysis and visualizations of the data.
    """)

with tab4:
    st.markdown("""
    ## References
    Data source: NYC Open Data.
    """)