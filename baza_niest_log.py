import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# 1. Konfiguracja strony i tła
st.set_page_config(page_title="LOG-PRO 4.0", layout="wide", page_icon="📦")

def apply_custom_design():
    st.markdown(f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.75)), 
        url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop");
        background-attachment: fixed; background-size: cover;
    }}
    [data-testid="stMetricValue"], .stMarkdown p {{ color: white !important; }}
    div[data-testid="stForm"] {{ 
        background-color: rgba(0, 0, 0, 0.6); 
        border-radius: 15px; padding: 20px; border: 1px solid #2e7d32; 
    }}
    </style>
    """, unsafe_allow_html=True)

apply_custom_design()

# 2. Połączenie z bazą Supabase
@st.cache_resource
def init_db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

db = init_db()

# 3. Funkcje pobierania danych
def load_warehouse_data():
    try:
        p = db.table("produkty").select("*, kategorie(nazwa)").execute()
        k = db.table("kategorie").select("*").execute()
        df_p = pd.DataFrame(p.data)
        if not df_p.empty:
            df_p['kat_nazwa'] = df_p['kategorie'].apply(lambda x: x['nazwa'] if isinstance(x, dict) else "Inne")
        return df_p, pd.DataFrame(k.data)
    except:
        return pd.DataFrame(), pd.DataFrame()

df_prod, df_kat = load_warehouse_data()

# 4. Główne Menu
st.title("🌐 LOG-PRO: Warehouse Command Center")

menu = st.sidebar.radio("Nawigacja", ["📊 Dashboard", "📦 Magazyn", "⚙️ Ustawienia"])

if menu == "📊 Dashboard":
    if not df_prod.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Liczba SKU", len(df_prod))
        c2.metric("Suma sztuk", int(df_prod['liczba'].sum()))
        c3.metric("Śr. Jakość", f"{df_prod['ocena'].mean():.1f} ⭐")
        
        st.subheader("Struktura zapasów")
        fig = px.bar(df_prod, x="kat_nazwa", y="liczba", color="ocena", template="dark")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Baza danych jest obecnie pusta.")

elif menu == "📦 Magazyn":
    t1, t2 = st.tabs(["Ewidencja", "Przyjęcie Towaru"])
    
    with t1:
        if not df_prod.empty:
            st.dataframe(df_prod[['nazwa', 'kat_nazwa', 'liczba', 'ocena']], use_container_width=True)
            if st.button("Usuń pierwszy produkt z listy"):
                db.table("produkty").delete
