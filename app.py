import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import os
from rapidfuzz import process, fuzz
import tempfile
from fpdf import FPDF

# Indlæs biblioteket direkte fra GitHub eller brugerupload
@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file, engine='openpyxl')
    else:
        url = "https://raw.githubusercontent.com/MalteKBK/indicator-search/main/Merged_Bibliotek.xlsx"
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        excel_data = BytesIO(response.content)
        df = pd.read_excel(excel_data, engine='openpyxl')
    # Fjern mellemrum fra kolonnenavne
    df.columns = [col.strip() for col in df.columns]
    return df

data = load_data()

# Brugernes tidligere søgninger
if 'history' not in st.session_state:
    st.session_state.history = []

# Fil upload
uploaded_file = st.file_uploader("Upload din egen Merged_Bibliotek.xlsx (med korrekte kolonnenavne)")
if uploaded_file is not None:
    data = load_data(uploaded_file)

# Søgning
st.title("🔍 Indikator Søgning for DGNB")
query = st.text_input("Søg efter produkt, produktnavn, producent eller materiale:")

selected_index = st.session_state.get("selected_index", None)
filtered_data = pd.DataFrame()  # Initialiser tomt DataFrame til senere brug

if query or selected_index is not None:
    # Hvis der er et valgt alternativ, brug det som hovedresultat
    if selected_index is not None:
        hoved_resultat = data.iloc[selected_index]
        st.session_state.selected_index = None  # Nulstil efter visning
    else:
        # Filtrer data baseret på direkte matches
        filtered_data = data[
            data.apply(lambda row: query.lower() in str(row).lower(), axis=1)
        ]
        
        if not filtered_data.empty:
            hoved_resultat = filtered_data.iloc[0]
        else:
            # Brug RapidFuzz til at finde det tætteste match
            choices = data['Relevante bygningsdele'].fillna('').tolist()
            match, score, index = process.extractOne(query, choices, scorer=fuzz.token_sort_ratio)
            hoved_resultat = data.iloc[index]
            st.warning(f"Ingen direkte match fundet. Det tætteste match er: {hoved_resultat['Indikator']} med beskrivelsen '{hoved_resultat['Relevante bygningsdele']}' (Sandsynlighed: {score}%)")
    
    # Gem søgning i historik
    st.session_state.history.append(query)
    
    # Vis hovedresultat
    st.markdown(f"<div style='background-color: #dfe7fd; padding: 20px; border-radius: 15px; margin-bottom: 20px;'>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='color: #1f3c88;'>✅ Indikatoren er sandsynligvis: {hoved_resultat['Indikator']}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p><strong>Beskrivelse:</strong> {hoved_resultat['Relevante bygningsdele'] or 'Ikke tilgængelig'}</p>", unsafe_allow_html=True)
    st.markdown(f"<p><strong>Produktets Kvalitetstrin:</strong> {hoved_resultat['Kvalitetstrin'] or 'Ikke tilgængelig'}</p>", unsafe_allow_html=True)
    st.markdown("<div style='display: flex; gap: 20px;'>", unsafe_allow_html=True)
    st.markdown(f"<div style='flex: 1; background-color: #f0f0f0; padding: 15px; border-radius: 10px;'><strong>Kvalitetstrin 1:</strong><br>{hoved_resultat['Krav til kvalitetstrin'] or 'Ikke tilgængelig'}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='flex: 1; background-color: #f0f0f0; padding: 15px; border-radius: 10px;'><strong>Kvalitetstrin 2:</strong><br>{hoved_resultat['Kvalitetstrin 2'] or 'Ikke tilgængelig'}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='flex: 1; background-color: #f0f0f0; padding: 15px; border-radius: 10px;'><strong>Kvalitetstrin 3:</strong><br>{hoved_resultat['Kvalitetstrin 3'] or 'Ikke tilgængelig'}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='flex: 1; background-color: #f0f0f0; padding: 15px; border-radius: 10px;'><strong>Kvalitetstrin 4:</strong><br>{hoved_resultat['Kvalitetstrin 4'] or 'Ikke tilgængelig'}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(f"<p><strong>Forklaring:</strong> Match fundet i: {', '.join([str(hoved_resultat[col]) for col in ['Materiale', 'Produktnavn', 'Producent', 'Kategori'] if pd.notna(hoved_resultat[col]) and query.lower() in str(hoved_resultat[col]).lower()])}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Eksport til PDF
    if st.button("📄 Eksportér resultat som PDF"):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, f"Indikator: {hoved_resultat['Indikator']}\nBeskrivelse: {hoved_resultat['Relevante bygningsdele']}\nKvalitetstrin: {hoved_resultat['Kvalitetstrin']}")
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf.output(temp_pdf.name)
        st.success("PDF eksporteret!")
        st.download_button("💾 Download PDF", temp_pdf.name, file_name="Indikator_Resultat.pdf")
