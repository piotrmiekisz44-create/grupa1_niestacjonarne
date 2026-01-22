import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

# 1. Konfiguracja strony
st.set_page_config(
    page_title="Logistics Intelligence Terminal", 
    page_icon="🚛", 
    layout="wide"
)

# --- CUSTOM CSS (WYSOKI KONTRAST I CZYTELNOŚĆ) ---
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
        url("https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075&auto=format&fit=crop");
        background-attachment: fixed;
        background-size: cover;
    }
    /* Kontener dla treści - czarne, półprzezroczyste tło dla czytelności tekstu */
    .main .block-container {
        background-color: rgba(0, 0, 0, 0.85);
        padding: 40px;
        border-radius: 20px;
        border: 2px solid #00d4ff;
        margin-top: 20px;
    }
    /* Metryki z mocnym obramowaniem */
    [data-testid="stMetric"] {
        background: #111;
        border: 2px solid #00ff88;
        border-radius: 10px;
        padding: 20px;
    }
    /* Nagłówki - biały tekst na ciemnym tle */
    h1, h2, h3 { 
        color: #ffffff !important; 
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    /* Opisy pól (help text) */
    .stMarkdown p {
        color: #e0e0e0 !important;
        font-size: 1.1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Połączenie z bazą
@st.cache_resource
def init_db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_db()

# 3. Pobieranie danych
@st.cache_data(ttl=5)
def get_data():
    try:
        p_res = supabase.table("produkty").select("*, kategorie(nazwa)").execute()
        k_res = supabase.table("kategorie").select("*").execute()
        df_p = pd.DataFrame(p_res.data)
        df_k = pd.DataFrame(k_res.data)
        if not df_p.empty and 'kategorie' in df_p.columns:
            df_p['kat_nazwa'] = df_p['kategorie'].apply(
                lambda x: x['nazwa'] if isinstance(x, dict) else "Nieprzypisane"
            )
        return df_p, df_k
    except
