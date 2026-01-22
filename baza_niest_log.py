import streamlit as st
from supabase import create_client, Client
import pandas as pd

# 1. Konfiguracja strony
st.set_page_config(page_title="Zarządzanie Magazynem", page_icon="📝", layout="wide")

# Inicjalizacja klienta Supabase
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# 2. Funkcja pobierania danych
def get_data():
    try:
        prod_resp = supabase.table("produkty").select("*, kategorie(nazwa)").execute()
        kat_resp = supabase.table("kategorie").select("*").execute()
        df_p = pd.DataFrame(prod_resp.data)
        df_k = pd.DataFrame(kat_resp.data)
        if not df_p.empty and 'kategorie' in df_p.columns:
            df_p['kat_nazwa'] = df_p['kategorie'].apply(lambda x: x['nazwa'] if isinstance(x, dict) else "Brak")
        return df_p, df_k
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame()

df_prod, df_kat = get_data()

# --- PANEL GŁÓWNY: DODAWANIE PRODUKTÓW ---
st.title("➕ Dodaj nowy produkt do bazy")

if not df_kat.empty:
    kat_options = {row['nazwa']: row['id'] for _, row in df_kat.iterrows()}
    
    # Formularz w ramce (container), aby oddzielić go od reszty
    with st.container(border=True):
        with st.form("main_add_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                n_prod = st.text_input("Nazwa produktu", placeholder="np. Laptop Dell")
                k_prod = st.selectbox("Kategoria", options=list(kat_options.keys()))
            with col2:
                l_prod = st.number_input("Ilość", min_value=0, step=1)
                o_prod = st.slider("Ocena (0-5)", 0.0, 5.0, 4.0, 0.1)
            
            submit = st.form_submit_button("Zapisz produkt w magazynie", use_container_width=True, type="primary")
            
            if submit:
                if n_prod:
                    supabase.table("produkty").insert({
                        "nazwa": n_prod, "liczba": l_prod, 
                        "ocena": o_prod, "kategoria_id": kat_options[k_prod]
                    }).execute()
                    st.success(f"Pomyślnie dodano: {n_prod}")
                    st.rerun()
                else:
                    st.error("Musisz podać nazwę produktu!")
else:
    st.warning("⚠️ Baza kategorii jest pusta. Dodaj kategorię w zakładce 'Ustawienia', aby móc dodawać produkty.")

st.divider()

# --- ZAKŁADKI Z ANALIZĄ I WYKRESAMI ---
tab_list, tab_charts, tab_settings = st.tabs(["📋 Lista Produktów", "📊 Wykresy i Statystyki", "⚙️ Ustawienia Kategorii"])

with tab_list:
    st.subheader("Aktualne stany magazynowe")
    if not df_prod.empty:
        df_view = df_prod[['nazwa', 'liczba', 'ocena', 'kat_nazwa']].copy()
        df_view.columns = ['Produkt', 'Ilość', 'Ocena
