import streamlit as st
from supabase import create_client, Client
import pandas as pd

# 1. Konfiguracja strony i połączenia
st.set_page_config(page_title="Magazyn Pro", page_icon="📦", layout="wide")

# Inicjalizacja klienta Supabase z Twoich Secrets
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# 2. Funkcja pobierania danych (z cache, aby aplikacja działała szybciej)
def get_data():
    try:
        # Pobieramy produkty wraz z danymi o kategoriach (join)
        prod_resp = supabase.table("produkty").select("*, kategorie(nazwa)").execute()
        kat_resp = supabase.table("kategorie").select("*").execute()
        
        df_p = pd.DataFrame(prod_resp.data)
        df_k = pd.DataFrame(kat_resp.data)
        
        # Przetwarzanie nazw kategorii dla wykresów
        if not df_p.empty and 'kategorie' in df_p.columns:
            df_p['kat_nazwa'] = df_p['kategorie'].apply(lambda x: x['nazwa'] if isinstance(x, dict) else "Brak")
            
        return df_p, df_k
    except Exception as e:
        st.error(f"Błąd połączenia z bazą: {e}")
        return pd.DataFrame(), pd.DataFrame()

df_prod, df_kat = get_data()

st.title("📦 System Zarządzania Magazynem")

# 3. Sekcja Analityczna (Dashboard)
st.subheader("📊 Podsumowanie Magazynu")
if not df_prod.empty:
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Liczba Produktów", len(df_prod))
    col_m2.metric("Suma Sztuk", int(df_prod['liczba'].sum()))
    col_m3.metric("Średnia Ocena", f"{df_prod['ocena'].mean():.2f} ⭐")

    # Wykres ilości produktów w podziale na kategorie
    st.write
