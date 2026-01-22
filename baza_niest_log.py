import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

# 1. Konfiguracja i Połączenie
st.set_page_config(page_title="LOG-PRO", layout="wide")

@st.cache_resource
def init_db():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_db()

# 2. Funkcje danych
def load_data():
    try:
        p = supabase.table("produkty").select("*, kategorie(nazwa)").execute()
        k = supabase.table("kategorie").select("*").execute()
        df_p = pd.DataFrame(p.data)
        df_k = pd.DataFrame(k.data)
        if not df_p.empty:
            df_p['kat_nazwa'] = df_p['kategorie'].apply(lambda x: x['nazwa'] if isinstance(x, dict) else "Inne")
        return df_p, df_k
    except:
        return pd.DataFrame(), pd.DataFrame()

df_p, df_k = load_data()

# 3. Interfejs
st.title("🌐 LOG-PRO: System Magazynowy")

menu = ["Podsumowanie", "Zasoby", "Ustawienia"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Podsumowanie":
    if not df_p.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Liczba SKU", len(df_p))
        c2.metric("Suma sztuk", int(df_p['liczba'].sum()))
        c3.metric("Śr. Jakość", f"{df_p['ocena'].mean():.1f}")
        
        st.subheader("Struktura zapasów")
        fig = px.pie(df_p, values='liczba', names='kat_nazwa', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Baza danych jest pusta.")

elif choice == "Zasoby":
    tab1, tab2 = st.tabs(["Lista produktów", "Dodaj nowy"])
    
    with tab1:
        if not df_p.empty:
            st.dataframe(df_p[['nazwa', 'kat_nazwa', 'liczba', 'ocena']], use_container_width=True)
            if st.button("Usuń zaznaczony (pierwszy z listy)"):
                supabase.table("produkty").delete().eq("id", df_p.iloc[0]['id']).execute()
                st.rerun()
                
    with tab2:
        with st.form("add_p"):
            name = st.text_input("Nazwa produktu")
            kat = st.selectbox("Kategoria", df_k['nazwa'].tolist() if not df_k.empty else
