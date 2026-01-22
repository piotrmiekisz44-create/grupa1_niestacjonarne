import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# 1. Połączenie (Supabase)
@st.cache_resource
def init_db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

db = init_db()

# 2. Ładowanie danych
def get_data():
    try:
        p = db.table("produkty").select("*, kategorie(nazwa)").execute()
        k = db.table("kategorie").select("*").execute()
        df_p = pd.DataFrame(p.data)
        if not df_p.empty:
            df_p['kat_nazwa'] = df_p['kategorie'].apply(lambda x: x['nazwa'] if isinstance(x, dict) else "Inne")
        return df_p, pd.DataFrame(k.data)
    except:
        return pd.DataFrame(), pd.DataFrame()

df_p, df_k = get_data()

# 3. Interfejs Użytkownika
st.set_page_config(page_title="LOG-PRO", layout="wide")
st.title("🌐 LOG-PRO: Warehouse Command Center")

page = st.sidebar.radio("Nawigacja", ["Raporty", "Magazyn", "System"])

if page == "Raporty":
    if not df_p.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("SKU", len(df_p))
        c2.metric("Sztuk", int(df_p['liczba'].sum()))
        c3.metric("Jakość", f"{df_p['ocena'].mean():.1f}")
        
        st.subheader("Struktura Kategorii")
        fig = px.bar(df_p, x="kat_nazwa", y="liczba", color="ocena", template="dark")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Brak danych.")

elif page == "Magazyn":
    t1, t2 = st.tabs(["Ewidencja", "Przyjęcie Towaru"])
    with t1:
        st.dataframe(df_p[['nazwa', 'kat_nazwa', 'liczba', 'ocena']], use_container_width=True)
        if st.button("Usuń pierwszy produkt"):
