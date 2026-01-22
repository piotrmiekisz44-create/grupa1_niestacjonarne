import streamlit as st
from supabase import create_client, Client
import pandas as pd

# 1. Konfiguracja strony - Profesjonalny Layout
st.set_page_config(
    page_title="Inwentaryzacja 4.0 Pro",
    page_icon="🚀",
    layout="wide"
)

# Inicjalizacja połączenia
@st.cache_resource
def init_connection():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Błąd konfiguracji: {e}")
        return None

supabase = init_connection()

# 2. Pobieranie danych (z cache dla szybkości)
@st.cache_data(ttl=10)
def fetch_data():
    if not supabase: return pd.DataFrame(), pd.DataFrame()
    try:
        p_res = supabase.table("produkty").select("*, kategorie(nazwa)").execute()
        k_res = supabase.table("kategorie").select("*").execute()
        
        df_p = pd.DataFrame(p_res.data)
        df_k = pd.DataFrame(k_res.data)
        
        if not df_p.empty and 'kategorie' in df_p.columns:
            # Mapowanie nazwy kategorii zgodnie ze schematem
            df_p['kat_nazwa'] = df_p['kategorie'].apply(
                lambda x: x['nazwa'] if isinstance(x, dict) else "Brak"
            )
        return df_p, df_k
    except Exception:
        return pd.DataFrame(), pd.DataFrame()

df_prod, df_kat = fetch_data()

# --- SIDEBAR: CENTRUM DOWODZENIA ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/database.png", width=80)
    st.title("System Magazynowy")
    st.markdown("---")
    menu = st.radio(
        "Główne moduły:",
        ["📈 Analityka", "📦 Inwentarz", "🛠️ Ustawienia"],
        index=0
    )
    st.markdown("---")
    st.success("Baza danych: POŁĄCZONO")
    if st.button("🔄 Odśwież system"):
        st.cache_data.clear()
