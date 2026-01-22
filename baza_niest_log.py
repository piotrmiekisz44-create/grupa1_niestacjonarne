import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="LOG-PRO COMMANDER", layout="wide")

# --- STYLE CSS (Uproszczone dla uniknięcia błędów składni) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    h1, h2 { color: #00ff88 !important; font-family: 'Arial'; }
    [data-testid="stMetric"] { 
        background-color: #1f2937; 
        border: 1px solid #00ff88; 
        padding: 15px; 
        border-radius: 10px; 
    }
    input, select { background-color: white !important; color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# --- POŁĄCZENIE Z BAZĄ ---
@st.cache_resource
def init_db():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Błąd połączenia: {e}")
        return None

supabase = init_db()

# --- POBIERANIE DANYCH ---
def get_data():
    if not supabase: return pd.DataFrame(), pd.DataFrame()
    try:
        p = supabase.table("produkty").select("*, kategorie(nazwa)").execute()
        k = supabase.table("kategorie").select("*").execute()
        df_p = pd.DataFrame(p.data)
        df_k = pd.DataFrame(k.data)
        if not df_p.empty:
            df_p['kat_nazwa'] = df_p['kategorie'].apply(lambda x: x['nazwa'] if isinstance(x, dict) else "Inne")
        return df_p, df_k
    except:
        return pd.DataFrame(), pd.DataFrame()

df_prod, df_kat = get_data()

# --- PASEK BOCZNY ---
with st.sidebar:
    st.title("🌐 LOG-PRO v3")
    page = st.radio("NAWIGACJA", ["Dashboard", "Zasoby", "K
