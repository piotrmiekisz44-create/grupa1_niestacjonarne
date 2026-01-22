import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="LOG-PRO 9.0", layout="wide")

# 1. DESIGN: Maksymalna widoczność (Neonowe kolory i wielkie czcionki)
st.markdown("""
<style>
.stApp { background-image: linear-gradient(rgba(0,0,0,0.85),rgba(0,0,0,0.85)), url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070"); background-size: cover; }
h1, h2, h3, label, p, .stMetric { color: #00FF00 !important; font-weight: 900 !important; font-size: 1.3rem !important; text-shadow: 2px 2px 4px #000; }
/* WIELKIE PRZYCISKI */
div.stButton > button:first-child { 
    background-color: #FFFF00 !important; color: #000 !important; font-size: 24px !important; 
    font-weight: 900 !important; border: 4px solid #FF00FF !important; border-radius: 20px !important;
    height: 80px !important; width: 100% !important; box-shadow: 0px 0px 15px #FF00FF;
}
div.stButton > button:first-child:hover { background-color: #FF00FF !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# 2. POŁĄCZENIE
@st.cache_resource
def init():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

db = init()

def get_data():
    try:
        p = db.table("produkty").select("*, kategorie(nazwa)").execute()
        k = db.table("kategorie").select("*").execute()
        df = pd.DataFrame(p.data)
        if not df.empty:
            df['kat'] = df['kategorie'].apply(lambda x: x['nazwa'] if isinstance(x, dict) else "Inne")
        return df, pd.DataFrame(k.data)
    except: return pd.DataFrame(), pd.DataFrame()

df_p, df_k = get_data()

# 3. INTERFEJS
st.title("🚢 LOG-PRO 9.0: WAREHOUSE COMMAND")
m = st.sidebar.radio("MODUŁ:", ["📊 STATYSTYKI", "📦 MAGAZYN", "⚙️ USTAWIENIA"])

if m == "📊 STATYSTYKI":
    if not df_p.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("SKU", len(df_p))
        c2.metric("SZTUKI", int(df_p['liczba'].sum()))
        c3.metric("JAKOŚĆ", f"{df_p['ocena'].mean():.1f}")
        
        # Bezpieczne wykresy statystyk
        st.subheader("STRUKTURA ZAPASÓW")
        fig1 = px.pie(df_p, names='kat', values='liczba', hole=0.4, template="dark")
        st.plotly_chart(fig1, use_container_width=True)
        
        st.subheader("ANALIZA JAKOŚCI")
        fig2 = px.bar(df_p, x='nazwa', y='liczba', color='ocena', template="dark")
        st.plotly_chart(fig2, use_container_width=True)
    else: st.warning("Baza jest pusta. Dodaj towar w zakładce MAGAZYN.")

elif m == "📦 MAGAZYN":
    t1, t2 = st.tabs(["🔍 STAN", "➕ DODAJ"])
    with t1:
        if not df_p.empty:
            st.dataframe(df_p[['nazwa', 'kat', 'liczba', 'ocena']], use_container_width=True)
            if st.button
