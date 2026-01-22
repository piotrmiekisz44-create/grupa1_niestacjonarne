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
    /* Import czcionki */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@300;500;700&display=swap');

    /* Tło i ogólny styl */
    .stApp {
        background-color: #05070a;
        background-image: 
            radial-gradient(at 0% 0%, rgba(0, 255, 136, 0.05) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(0, 212, 255, 0.05) 0px, transparent 50%);
    }

    /* Szklany kontener główny */
    .main .block-container {
        background: rgba(13, 17, 23, 0.7);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(0, 255, 136, 0.2);
        border-radius: 30px;
        padding: 50px;
        box-shadow: 0 0 50px rgba(0,0,0,0.5);
    }

    /* Nagłówki Sci-Fi */
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 3px;
        color: #00ff88 !important;
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
    }

    /* Karty Metryk z animacją */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(0, 255, 136, 0.1), rgba(0, 212, 255, 0.1));
        border: 1px solid rgba(0, 255, 136, 0.3);
        border-radius: 20px;
        padding: 25px !important;
        transition: all 0.4s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: scale(1.05);
        border-color: #00ff88;
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
    }

    /* Inputy - Wysoki Kontrast (Czarne na białym dla czytelności) */
    input, select, textarea, div[data-baseweb="select"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        border-radius: 10px !important;
        font-weight: bold !important;
    }

    /* Przyciski - Neonowe */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #00ff88, #00d4ff) !important;
        color: #000000 !important;
        font-family: 'Orbitron', sans-serif;
        font-weight: bold;
        border: none !important;
        padding: 15px !important;
        border-radius: 12px !important;
        transition: 0.3s !important;
    }
    .stButton>button:hover {
        box-shadow: 0 0 25px #00ff88;
        transform: translateY(-2px);
    }

    /* SideBar */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 2px solid #00ff88;
    }

    /* Tabele (Dataframe) */
    .stDataFrame {
        border-radius: 15px;
        overflow: hidden;
        border: 1px solid rgba(0, 255, 136, 0.2);
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
    except:
        st.error("📡 Błąd 404: System nie może połączyć się z serwerem bazy danych.")
        return None

supabase = init_connection()

# --- 4. LOGIKA POBIERANIA DANYCH ---
def get_data():
    if not supabase: return pd.DataFrame(), pd.DataFrame()
    p_req = supabase.table("produkty").select("*, kategorie(nazwa)").execute()
    k_req = supabase.table("kategorie").select("*").execute()
    df_p = pd.DataFrame(p_req.data)
    df_k = pd.DataFrame(k_req.data)
    if not df_p.empty:
        df_p['kat_nazwa'] = df_p['kategorie'].apply(lambda x: x['nazwa'] if isinstance(x, dict) else "Niezdefiniowana")
    return df_p, df_k

df_prod, df_kat = get_data()

# --- 5. SIDEBAR - MENU STEROWANIA ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🌐 LOG-PRO OS</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #00ff88;'>System Zarządzania Klasy S</p>", unsafe_allow_html=True)
    st.divider()
    
    choice = st.selectbox("WYBIERZ MODUŁ:", [
        "🛸 Terminal Główny", 
        "📦 Zarządzanie SKU", 
        "🧮 Centrum Kosztów",
        "🛠️ Inżynieria Systemu"
    ])
    
    st.divider()
    # Dynamiczny zegar i status
    st.write(f"🕒 Time: {datetime.now().strftime('%H:%M:%S')}")
    st.success("STATUS: ONLINE")

# --- 6. MODUŁ 1: TERMINAL GŁÓWNY (DASHBOARD BI) ---
if choice == "🛸 Terminal Główny":
    st.title("🛸 Globalny Terminal Operacyjny")
    
    if not df_prod.empty:
        # Metryki KPI
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("SKU TOTAL", len(df_prod), "items")
        m2.metric("WOLUMEN TOTAL", int(df_prod['liczba'].sum()), "units")
        m3.metric("AVG QUALITY", f"{df_prod['ocena'].mean():.2f}", "stars")
        
        low_stock = len(df_prod[df_prod['liczba'] < 15])
        m4.metric("ALERTY BRAKU", low_stock, delta=f"-{low_stock}", delta_color="inverse")

        st.divider()
        
        col_l, col_r = st.columns([3, 2])
        
        with col_l:
            st.subheader("📍 Mapa Cieplna Magazynu (Treemap)")
            fig_tree = px.treemap(df_prod, path=['kat_nazwa', 'nazwa'], values='liczba',
                                 color='ocena', color_continuous_scale='RdYlGn',
                                 hover_data=['liczba'], template="plotly_dark")
            fig_tree.update_layout(margin=dict(t=0, l=0, r=0, b=0))
            st.plotly_chart(fig
