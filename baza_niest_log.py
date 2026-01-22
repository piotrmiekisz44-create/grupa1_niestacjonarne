import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# 1. Połączenie z bazą danych
@st.cache_resource
def init_db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

db = init_db()

# 2. Pobieranie danych z Supabase
def get_data():
    try:
        p_req = db.table("produkty").select("*, kategorie(nazwa)").execute()
        k_req = db.table("kategorie").select("*").execute()
        df_p = pd.DataFrame(p_req.data)
        df_k = pd.DataFrame(k_req.data)
        if not df_p.empty:
            df_p['kat_nazwa'] = df_p['kategorie'].apply(lambda x: x['nazwa'] if isinstance(x, dict) else "Inne")
        return df_p, df_k
    except:
        return pd.DataFrame(), pd.DataFrame()

df_prod, df_kat = get_data()

# 3. Konfiguracja strony i Interfejs
st.set_page_config(page_title="LOG-PRO", layout="wide")
st.title("📦 LOG-PRO: Warehouse Command Center")

strona = st.sidebar.radio("Nawigacja", ["Dashboard", "Magazyn", "Ustawienia"])

if strona == "Dashboard":
    if not df_prod.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Liczba SKU", len(df_prod))
        c2.metric("Suma sztuk", int(df_prod['liczba'].sum()))
        c3.metric("Śr. Jakość", f"{df_prod['ocena'].mean():.1f}")
        
        st.subheader("Struktura Kategorii")
        fig = px.pie(df_prod, values='liczba', names='kat_nazwa', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Brak towarów w bazie danych.")

elif strona == "Magazyn":
    t1, t2 = st.tabs(["Lista towarów", "Przy
