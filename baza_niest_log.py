import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

# --- KONFIGURACJA WIZUALNA ---
st.set_page_config(page_title="Warehouse Intel OS", page_icon="🕋", layout="wide")

# Zaawansowana stylizacja CSS (Ciemny motyw magazynu)
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), 
        url("https://images.unsplash.com/photo-1587293855946-b52c974416ae?q=80&w=2070");
        background-attachment: fixed;
        background-size: cover;
    }
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 15px;
        padding: 15px;
    }
    h1, h2, h3 { color: #00d4ff !important; text-shadow: 2px 2px 5px #000; }
    </style>
    """, unsafe_allow_html=True)

# Połączenie z Supabase
@st.cache_resource
def init_db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_db()

# Pobieranie danych
@st.cache_data(ttl=5)
def get_warehouse_data():
    try:
        # Relacja produktów i kategorii
        p_res = supabase.table("produkty").select("*, kategorie(nazwa)").execute()
        k_res = supabase.table("kategorie").select("*").execute()
        df_p = pd.DataFrame(p_res.data)
        df_k = pd.DataFrame(k_res.data)
        if not df_p.empty and 'kategorie' in df_p.columns:
            df_p['kat_nazwa'] = df_p['kategorie'].apply(lambda x: x['nazwa'] if isinstance(x, dict) else "Brak")
        return df_p, df_k
    except:
        return pd.DataFrame(), pd.DataFrame()

df_prod, df_kat = get_warehouse_data()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🕋 WI-OS v4.2</h1>", unsafe_allow_html=True)
    menu = st.radio("MODUŁY:", ["📊 Dashboard", "📦 Inwentarz", "📈 Predykcja", "⚙️ Baza"])
    st.divider()
    st.success("POŁĄCZENIE AKTYWNE")

# --- MODUŁY ---
if menu == "📊 Dashboard":
    st.title("📊 Warehouse Real-time Dashboard")
    if not df_prod.empty:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Asortyment", len(df_prod))
        c2.metric("Suma Zapasu", int(df_prod['liczba'].sum()))
        c3.metric("Średnia Jakość", f"{df_prod['ocena'].mean():.2f}")
        low = len(df_prod[df_prod['liczba'] < 5])
        c4.metric("Krytyczne Braki", low, delta=f"-{low}", delta_color="inverse")

        col_l, col_r = st.columns(2)
        with col_l:
            fig1 = px.bar(df_prod.groupby('kat_nazwa')['liczba'].sum().reset_index(), 
                         x='kat_nazwa', y='liczba', color='liczba',
                         title="Stany wg Kategorii", template="plotly_dark",
                         color_continuous_scale='Blues')
            st.plotly_chart(fig1, use_container_
