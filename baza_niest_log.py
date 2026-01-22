import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

# --- KONFIGURACJA WIZUALNA ---
st.set_page_config(
    page_title="LOG-PRO: Logistics Intelligence", 
    page_icon="🚢", 
    layout="wide"
)

# --- STYLIZACJA CSS (WYSOKI KONTRAST I CZYTELNOŚĆ) ---
st.markdown("""
    <style>
    /* Tło aplikacji */
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), 
        url("https://images.unsplash.com/photo-1494412519320-aa613dfb7738?q=80&w=2070");
        background-attachment: fixed;
        background-size: cover;
    }

    /* GŁÓWNY KONTENER TREŚCI */
    .main .block-container {
        background-color: rgba(20, 20, 20, 0.95);
        padding: 40px;
        border-radius: 15px;
        border: 1px solid #00ff88;
    }

    /* POLA TEKSTOWE I INPUTY - Białe tło, czarny tekst dla czytelności */
    input, select, textarea, .stSelectbox, .stNumberInput, .stTextInput {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 5px !important;
    }
    
    /* Naprawa koloru tekstu wewnątrz pól wpisywania */
    div[data-baseweb="input"] input, div[data-baseweb="select"] {
        color: #000000 !important;
        background-color: #FFFFFF !important;
    }

    /* ETYKIETY PÓL (Labelki) - Jasny turkus dla kontrastu */
    label, .stMarkdown p {
        color: #00d4ff !important;
        font-weight: 700 !important;
        text-shadow: 1px 1px 2px #000;
    }

    /* PRZYCISKI - Bardziej widoczne */
    .stButton>button {
        background-color: #00ff88 !important;
        color: #000000 !important;
        font-weight: bold !important;
        border: 2px solid #FFFFFF !important;
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #00d4ff !important;
        transform: scale(1.02);
    }

    /* TABELE I DATAFRAME - Jasne tło, ciemny tekst */
    .stDataFrame, [data-testid="stTable"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 10px;
        padding: 10px;
    }

    /* SIDEBAR (MENU BOCZNE) - Głęboka czerń */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 2px solid #00ff88;
    }
    
    /* NAGŁÓWKI */
    h1, h2, h3 { 
        color: #00ff88 !important; 
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICJALIZACJA BAZY ---
@st.cache_resource
def init_db():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
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
        k_res = supabase.table("kategorie").select("*").execute()
        df_p = pd.DataFrame(p_res.data)
        df_k = pd.DataFrame(k_res.data)
        
        if not df_p.empty and 'kategorie' in df_p.columns:
            df_p['kat_nazwa'] = df_p['kategorie'].apply(
                lambda x: x['nazwa'] if isinstance(x, dict) else "Brak"
            )
        return df_p, df_k
    except Exception:
        return pd
