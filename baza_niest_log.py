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

# --- STYLIZACJA CSS (CZARNE CZCIONKI I JASNA CZYTELNOŚĆ) ---
st.markdown("""
    <style>
    /* Tło i główny kontener */
    .stApp {
        background-image: linear-gradient(rgba(255,255,255,0.8), rgba(255,255,255,0.8)), 
        url("https://images.unsplash.com/photo-1494412519320-aa613dfb7738?q=80&w=2070");
        background-attachment: fixed;
        background-size: cover;
    }

    /* Panele i kontenery */
    [data-testid="stSidebar"] {
        background-color: #f1f3f6 !important;
        border-right: 3px solid #00ff88;
    }
    
    .main .block-container {
        background-color: rgba(255, 255, 255, 0.96);
        padding: 40px;
        border-radius: 20px;
        border: 1px solid #dee2e6;
    }

    /* WYMUSZENIE CZARNEJ CZCIONKI DLA WSZYSTKIEGO */
    html, body, [class*="st-"], .stMarkdown p, label, .stMetric div, h1, h2, h3 {
        font-family: 'Segoe UI', sans-serif;
        color: #000000 !important;
    }

    h1, h2, h3 { 
        text-transform: uppercase;
        font-weight: 800;
    }

    /* Pola wprowadzania danych */
    input, textarea, select, div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #00ff88 !important;
        border-radius: 8px !important;
    }

    /* Metryki */
    [data-testid="stMetric"] {
        background: #ffffff;
        border-left: 5px solid #00ff88;
        border-radius: 8px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }

    /* Przyciski */
    .stButton>button {
        background-color: #00ff88 !important;
        color: #000000 !important;
        font-weight: 900 !important;
        border-radius: 10px !important;
        border: 2px solid #000000 !important;
    }

    /* Poprawa widoczności tabel */
    [data-testid="stTable"], .stDataFrame {
        background-color: white !important;
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
        return pd.DataFrame(), pd.DataFrame()

df_prod, df_kat = get_data()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: black !important;'>🚢 LOG-PRO</h1>", unsafe_allow_html=True)
    menu = st.radio(
        "WYBIERZ MODUŁ:", 
        ["📊 Dashboard", "📦 Inwentarz", "⚙️ Konfiguracja"]
    )
    st.divider()
    st.success("STATUS: POŁĄCZONO")

# --- MODUŁ 1: DASHBOARD ---
if menu == "📊 Dashboard":
    st.title("📊 Statystyki Magazynowe")
    if not df_prod.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Pozycje (SKU)", len(df_prod))
        c2.metric("Suma Sztuk", int(df_prod['liczba'].sum()))
        c3.metric("Średnia Jakość", f"{df_prod['ocena'].mean():.2f}")

        st.divider()
        col_l, col_r = st.columns(2)
        with col_l:
            fig1 = px.bar(
                df_prod.groupby('kat_nazwa')['liczba'].sum().reset_index(), 
                x='kat_nazwa', y='liczba', color='liczba',
                template="plotly_white", title="Stany wg Kategorii"
            )
            st.plotly_chart(fig1, use_container_width=True)
        with col_r:
            fig2 = px.pie(
                df_prod, names='kat_nazwa', values='liczba', hole=
