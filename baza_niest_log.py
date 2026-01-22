import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Konfiguracja strony
st.set_page_config(
    page_title="Warehouse Intelligence OS v4.0",
    page_icon="🕋",
    layout="wide"
)

# --- CUSTOM CSS (TŁO I STYLIZACJA) ---
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
        url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop");
        background-attachment: fixed;
        background-size: cover;
    }
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    h1, h2, h3 {
        color: #00d4ff !important;
        text-shadow: 2px 2px 4px #000000;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: rgba(0,0,0,0.3);
        padding: 10px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Połączenie z bazą
@st.cache_resource
def init_connection():
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except:
        st.error("Błąd połączenia z bazą danych!")
        return None

supabase = init_connection()

# 3. Pobieranie danych
@st.cache_data(ttl=5)
def fetch_data():
    if not supabase: return pd.DataFrame(), pd.DataFrame()
    p_res = supabase.table("produkty").select("*, kategorie(nazwa)").execute()
    k_res = supabase
