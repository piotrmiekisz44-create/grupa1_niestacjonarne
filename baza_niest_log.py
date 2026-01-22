import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

# --- KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="LOG-PRO: Logistics Intelligence", 
    page_icon="🚢", 
    layout="wide"
)

# --- STYLIZACJA CSS (CIEMNY SIDEBAR I WYSOKI KONTRAST) ---
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.75)), 
        url("https://images.unsplash.com/photo-1494412519320-aa613dfb7738?q=80&w=2070");
        background-attachment: fixed;
        background-size: cover;
    }

    [data-testid="stSidebar"] {
        background-color: #050505 !important;
        border-right: 2px solid #00ff88;
    }
    
    .main .block-container {
        background-color: rgba(0, 0, 0, 0.9);
        padding: 50px;
        border-radius: 20px;
        border: 1px solid rgba(0, 212, 255, 0.2);
    }

    html, body, [class*="st-"] {
        font-family: 'Segoe UI', Helvetica, sans-serif;
        color: #FFFFFF !important;
        line-height: 1.7;
    }

    h1, h2, h3 { 
        color: #00ff88 !important; 
        font-weight: 800 !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }

    .stTextInput label, .stSelectbox label, .stNumberInput label, .stSlider label {
        color: #00d4ff !important;
        font-weight: 700 !important;
    }

    [data-testid="stMetric"] {
        background: #111111;
        border: 2px solid #00ff88;
        border-radius: 12px;
        padding: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICJALIZACJA BAZY ---
@st.cache_resource
def init_db():
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except Exception as e:
        st.error(f"Problem z połączeniem: {e}")
        return None

supabase = init_db()

# --- POBIERANIE DANYCH ---
@st.cache_data(ttl=5)
def get_data():
    if not supabase: 
        return pd.DataFrame(), pd.DataFrame()
    try:
        p_res = supabase.table("produkty").select("*, kategorie(nazwa)").execute()
        k_res =
