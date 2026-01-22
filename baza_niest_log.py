import streamlit as st
from supabase import create_client, Client
import pandas as pd

# 1. Konfiguracja "WOW" - Profesjonalny interfejs
st.set_page_config(
    page_title="Inwentaryzacja 4.0 | Panel Zarządzania",
    page_icon="🚀",
    layout="wide"
)

# --- DODAWANIE TŁA LOGISTYCZNEGO ---
def add_bg_from_url():
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
             url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop");
             background-attachment: fixed;
             background-size: cover;
         }}
         
         /* Poprawa czytelności kart i kontenerów */
         [data-testid="stMetricValue"], [data-testid="stMarkdownContainer"] p {{
             color: white !important;
         }}
         
         .stTabs [data-baseweb="tab-list"] {{
             background-color: rgba(255, 255, 255, 0.1);
             border-radius: 10px;
             padding: 5px;
         }}

         div[data-testid="stForm"] {{
             background-color: rgba(0, 0, 0, 0.6);
             border: 1px solid #2e7d32;
             border-radius: 15px;
             padding: 20px;
         }}
         
         header, .stSidebar {{
             background-color: rgba(0, 0, 0, 0.8) !important;
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

add_bg_from_url()

# Inicjalizacja połączenia
@st.cache_resource
def init_connection():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Krytyczny błąd konfiguracji: {e}")
        return None

supabase = init_connection()

# 2. Pobieranie danych z cache
@st.cache_data(ttl=10)
def fetch_data():
    if not supabase: return pd.DataFrame(), pd.DataFrame()
    try:
        p_res = supabase.table("produkty").select("*, kategorie(nazwa)").execute()
        k_res = supabase.table("kategorie").select("*").execute()
        
        df_p = pd.DataFrame(p_res.data)
        df_k = pd.DataFrame(k_res.data)
        
        if not df_p.empty and 'kategorie'
