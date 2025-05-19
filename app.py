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
            st.markdown(f"### Indikator: {row['Indikator']}")
            st.markdown(f"**Beskrivelse:** {row['Relevante bygningsdele'] or 'Ikke tilgængelig'}")
            st.markdown(f"**Kvalitetstrin 1:** {row['Krav til kvalitetstrin'] or 'Ikke tilgængelig'}")
            st.markdown(f"**Kvalitetstrin 2:** {row['Kvalitetstrin 2'] or 'Ikke tilgængelig'}")
            st.markdown(f"**Kvalitetstrin 3:** {row['Kvalitetstrin 3'] or 'Ikke tilgængelig'}")
            st.markdown(f"**Kvalitetstrin 4:** {row['Kvalitetstrin 4'] or 'Ikke tilgængelig'}")
            st.markdown(f"**Forklaring:** Match fundet i: {', '.join([str(row[col]) for col in ['Materiale', 'Produktnavn', 'Producent', 'Kategori'] if pd.notna(row[col]) and query.lower() in str(row[col]).lower()])}")
            st.markdown("---")
    else:
        st.warning("Ingen relevante indikatorer fundet.")
