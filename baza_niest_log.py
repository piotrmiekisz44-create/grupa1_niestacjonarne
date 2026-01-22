import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# 1. Połączenie z bazą
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# 2. Pobieranie danych
def load_data():
    try:
        p = supabase.table("produkty").select("*, kategorie(nazwa)").execute()
        k = supabase.table("kategorie").select("*").execute()
        df_p = pd.DataFrame(p.data)
        if not df_p.empty:
            df_p['kat_nazwa'] = df_p['kategorie'].apply(lambda x: x['nazwa'] if isinstance(x, dict) else "Inne")
        return df_p, pd.DataFrame(k.data)
    except Exception as e:
        st.error(f"Błąd bazy: {e}")
        return pd.DataFrame(), pd.DataFrame()

df_prod, df_kat = load_data()

# 3. Interfejs Użytkownika
st.title("📦 System LOG-PRO")

strona = st.sidebar.radio("MENU", ["Panel Główny", "Magazyn", "Konfiguracja"])

if strona == "Panel Główny":
    if not df_prod.empty:
        c1, c2 = st.columns(2)
        c1.metric("Liczba SKU", len(df_prod))
        c2.metric("Suma sztuk", int(df_prod['liczba'].sum()))
        
        fig = px.pie(df_prod, names='kat_nazwa', values='liczba', title="Udział kategorii")
        st.plotly_chart(fig)
    else:
        st.info("Baza jest pusta.")

elif strona == "Magazyn":
    tab1, tab2 = st.tabs(["Lista", "Dodaj produkt"])
    with tab1:
        st.dataframe(df_prod[['nazwa', 'kat_nazwa', 'liczba', 'ocena']], use_container_width=True)
        if not df_prod.empty:
            if st.button("Usuń pierwszy produkt"):
                supabase.table("produkty").delete().eq("id", df_prod.iloc[0]['id']).execute()
                st.rerun()
    with tab2:
        with st.form("form_dodaj"):
            n = st.text_input("Nazwa")
            k = st.selectbox("Kategoria", df_kat['nazwa'].tolist() if not df_kat.empty else ["Brak"])
            l = st.number_input("Ilość", min_value=1)
            o = st.slider("Ocena jakości", 1, 5,
