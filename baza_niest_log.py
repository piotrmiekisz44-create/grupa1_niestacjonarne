import streamlit as st
from supabase import create_client, Client
import pandas as pd

# 1. Konfiguracja strony
st.set_page_config(
    page_title="Warehouse Manager Pro",
    page_icon="🏢",
    layout="wide"
)

# Inicjalizacja połączenia z Supabase
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# 2. Pobieranie danych z cache
@st.cache_data(ttl=10)
def fetch_warehouse_data():
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

df_prod, df_kat = fetch_warehouse_data()

# --- SIDEBAR: NAWIGACJA ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/box.png", width=60)
    st.title("Warehouse Pro")
    menu = st.radio(
        "Nawigacja:",
        ["📊 Dashboard", "📦 Produkty", "⚙️ Ustawienia Kategorii"]
    )
    st.divider()
    st.caption("Status: Połączono z Supabase")

# --- MODUŁ 1: DASHBOARD ---
if menu == "📊 Dashboard":
    st.header("📊 Statystyki Magazynowe")
    
    if not df_prod.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Liczba Produktów", len(df_prod))
        c2.metric("Suma Sztuk", int(df_prod['liczba'].sum()))
        c3.metric("Średnia Ocena", f"{df_prod['ocena'].mean():.2f} ⭐")
        
        col_left, col_right = st.columns(2)
        with col_left:
            st.subheader("Stany wg Kategorii")
            st.bar_chart(df_prod.groupby('kat_nazwa')['liczba'].sum())
        with col_right:
            st.subheader("Rozkład Ocen")
            st.area_chart(df_prod['ocena'].value_counts().sort_index())
    else:
        st.info("Baza danych jest pusta.")

# --- MODUŁ 2: PRODUKTY (Linia 77 - Tutaj był błąd) ---
elif menu == "📦 Produkty":
    st.header("📦 Zarządzanie Produktami")
    
    tab_list, tab_add = st.tabs(["📋 Przeglądaj", "➕ Dodaj Nowy"])
    
    with tab_list:
        if not df_prod.empty:
            df_display = df_prod[['nazwa', 'liczba', 'ocena', 'kat_nazwa']].copy()
            df_display.columns = ['Nazwa', 'Liczba', 'Ocena', 'Kategoria']
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            with st.expander("Usuń produkt"):
                to_del = st.selectbox("Wybierz produkt", df_prod['nazwa'].tolist())
                if st.button("Usuń trwale", type="secondary"):
                    id_d = df_prod[df_prod['nazwa'] == to_del]['id'].values[0]
                    supabase.table("produkty").delete().eq("id", id_d).execute()
                    st.cache_data.clear()
                    st.rerun()
        else:
            st.write("Brak produktów.")

    with tab_add:
        if not df_kat.empty:
            kat_map = {r['nazwa']: r['id'] for _, r in df_kat.
