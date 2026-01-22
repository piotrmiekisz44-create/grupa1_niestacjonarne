import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# 1. Połączenie
@st.cache_resource
def init_db():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

db = init_db()

# 2. Pobieranie danych
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

df_p, df_k = get_data()

# 3. Interfejs
st.title("📡 LOG-PRO Terminal")

menu = st.sidebar.radio("Nawigacja", ["Dashboard", "Magazyn", "Ustawienia"])

if menu == "Dashboard":
    if not df_p.empty:
        c1, c2 = st.columns(2)
        c1.metric("Suma SKU", len(df_p))
        c2.metric("Suma Sztuk", int(df_p['liczba'].sum()))
        
        fig = px.pie(df_p, values='liczba', names='kat_nazwa', title="Podział zapasów")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Brak danych w bazie.")

elif menu == "Magazyn":
    st.subheader("Lista towarów")
    if not df_p.empty:
        st.dataframe(df_p[['nazwa', 'kat_nazwa', 'liczba', 'ocena']], use_container_width=True)
    
    st.divider()
    st.subheader("Dodaj nowy towar")
    with st.form("dodaj"):
        n = st.text_input("Nazwa")
        k = st.selectbox("Kategoria", df_k['nazwa'].tolist() if not df_k.empty else ["Brak"])
        l = st.number_input("
