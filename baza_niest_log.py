import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

# --- KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="LOG-PRO: System Logistyczny", 
    page_icon="🚢", 
    layout="wide"
)

# --- STYLIZACJA CSS (ZAKCENTOWANE POLA TEKSTOWE) ---
st.markdown("""
    <style>
    /* Tło i główny kontener */
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), 
        url("https://images.unsplash.com/photo-1494412519320-aa613dfb7738?q=80&w=2070");
        background-attachment: fixed;
        background-size: cover;
    }

    /* Panele i kontenery */
    [data-testid="stSidebar"] {
        background-color: #050505 !important;
        border-right: 2px solid #00ff88;
    }
    
    .main .block-container {
        background-color: rgba(0, 0, 0, 0.92);
        padding: 40px;
        border-radius: 20px;
        border: 1px solid rgba(0, 212, 255, 0.3);
    }

    /* Teksty ogólne */
    html, body, [class*="st-"] {
        font-family: 'Segoe UI', sans-serif;
        color: #FFFFFF !important;
    }

    h1, h2, h3 { 
        color: #00ff88 !important; 
        text-transform: uppercase;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }

    /* KLUCZOWE: Stylizacja pól tekstowych i liczbowych */
    input, textarea, select, div[data-baseweb="select"] > div {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border: 2px solid #00ff88 !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        font-size: 16px !important;
    }

    /* Stylizacja etykiet nad polami (Label) */
    .stMarkdown p, label {
        color: #00ff88 !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }

    /* Fokus na polach (po kliknięciu) */
    input:focus, textarea:focus {
        border-color: #00d4ff !important;
        box-shadow: 0 0 10px #00d4ff !important;
    }

    /* Metryki */
    [data-testid="stMetric"] {
        background: #111;
        border: 2px solid #00ff88;
        border-radius: 12px;
        padding: 15px;
    }

    /* Przyciski */
    .stButton>button {
        background-color: #00ff88 !important;
        color: #000000 !important;
        font-weight: 900 !important;
        border-radius: 10px !important;
        border: none !important;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #00d4ff !important;
        transform: scale(1.02);
    }
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
@st.cache_data(ttl=5)
def get_data():
