import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# Indlæs biblioteket direkte fra GitHub
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/MalteKBK/indicator-search/main/Merged_Bibliotek.xlsx"
    response = requests.get(url)
    response.raise_for_status()  # Check for HTTP errors
    excel_data = BytesIO(response.content)
    df = pd.read_excel(excel_data, engine='openpyxl')
    # Fjern mellemrum fra kolonnenavne
    df.columns = [col.strip() for col in df.columns]
    return df

data = load_data()

# Søgning
st.title("Indikator Søgning")
query = st.text_input("Søg efter produkt, produktnavn, producent eller materiale:")

if query:
    # Filtrer data baseret på søgningen
    filtered_data = data[
        data.apply(lambda row: query.lower() in str(row).lower(), axis=1)
    ]
    
    # Hvis der er resultater, vis dem
    if not filtered_data.empty:
        for _, row in filtered_data.iterrows():
            st.markdown(f"## Indikatoren er sandsynligvis: {row['Indikator']}")
            st.markdown(f"**Beskrivelse:** {row['Relevante bygningsdele'] or 'Ikke tilgængelig'}")
            
            # Resultatboks for kvalitetstrin
            st.markdown("<div style='display: flex; gap: 20px;'>", unsafe_allow_html=True)
            st.markdown(f"<div style='flex: 1; background-color: #f0f0f0; padding: 15px; border-radius: 10px;'><strong>Kvalitetstrin 1:</strong><br>{row['Krav til kvalitetstrin'] or 'Ikke tilgængelig'}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='flex: 1; background-color: #f0f0f0; padding: 15px; border-radius: 10px;'><strong>Kvalitetstrin 2:</strong><br>{row['Kvalitetstrin 2'] or 'Ikke tilgængelig'}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='flex: 1; background-color: #f0f0f0; padding: 15px; border-radius: 10px;'><strong>Kvalitetstrin 3:</strong><br>{row['Kvalitetstrin 3'] or 'Ikke tilgængelig'}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='flex: 1; background-color: #f0f0f0; padding: 15px; border-radius: 10px;'><strong>Kvalitetstrin 4:</strong><br>{row['Kvalitetstrin 4'] or 'Ikke tilgængelig'}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown(f"**Forklaring:** Match fundet i: {', '.join([str(row[col]) for col in ['Materiale', 'Produktnavn', 'Producent', 'Kategori'] if pd.notna(row[col]) and query.lower() in str(row[col]).lower()])}")
            st.markdown("---")
    else:
        st.warning("Ingen relevante indikatorer fundet.")
