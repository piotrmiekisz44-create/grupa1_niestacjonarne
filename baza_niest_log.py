import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# --- 1. KONFIGURACJA ŚRODOWISKA ---
st.set_page_config(
    page_title="LOG-PRO COMMAND CENTER",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. FUTURYSTYCZNY DESIGN CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@300;500;700&display=swap');

    .stApp {
        background-color: #05070a;
        background-image: 
            radial-gradient(at 0% 0%, rgba(0, 255, 136, 0.05) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(0, 212, 255, 0.05) 0px, transparent 50%);
    }

    .main .block-container {
        background: rgba(13, 17, 23, 0.7);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(0, 255, 136, 0.2);
        border-radius: 30px;
        padding: 50px;
    }

    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 3px;
        color: #00ff88 !important;
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(0, 255, 136, 0.1), rgba(0, 212, 255, 0.1));
        border: 1px solid rgba(0, 255, 136, 0.3);
        border-radius: 20px;
        padding: 25px !important;
    }

    input, select, textarea, div[data-baseweb="select"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        border-radius: 10px !important;
        font-weight: bold !important;
    }

    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #00ff88, #00d4ff) !important;
        color: #000000 !important;
        font-family: 'Orbitron', sans-serif;
        font-weight: bold;
        border: none !important;
        border-radius: 12px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. POŁĄCZENIE Z BAZĄ DANYCH ---
@st.cache_resource
def init_connection():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Błąd połączenia: {e}")
        return None

supabase = init_
