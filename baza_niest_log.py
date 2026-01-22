import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="LOG-PRO 10.0", layout="wide")

# 1. MEGA DESIGN: Neonowe przyciski i czytelne teksty
st.markdown("""
<style>
.stApp { background: linear-gradient(rgba(0,0,0,0.8),rgba(0,0,0,0.8)), url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=1000"); background-size: cover; }
h1, h2, label, p, .stMetric { color: #00FF00 !important; font-weight: 900 !important; text-shadow: 2px 2px #000; font-size: 1.2rem !important; }
/* PRZYCISKI GIGANTY */
div.stButton > button { 
    background: #FFFF00 !important; color: #000 !important; font-size: 25px !important; 
    font-weight: 900 !important; border: 5px solid #FF00FF !important; border-radius: 20px !important;
    height: 70px !important; width: 100% !important; box-shadow: 0 0 20px #FF00FF;
}
div.stButton > button:hover { background: #FF00FF !important; color: #fff !important; }
</style>
""", unsafe_allow_html=True)

# 2. BAZA DANYCH
@st.cache_resource
def init():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

db = init()

def load():
    try:
        p = db.table("produkty").select("*, kategorie(nazwa)").execute()
        k = db.table("kategorie").select("*").execute()
        df = pd.DataFrame(p.data)
        if not df.empty:
            df['kat_n'] = df['kategorie'].apply(lambda x: x['nazwa'] if isinstance(x, dict) else "Inne")
        return df, pd.DataFrame(k.data)
    except: return pd.DataFrame(), pd.DataFrame()

df_p, df_k = load()

# 3. INTERFEJS GŁÓWNY
st.title("🚢 LOG-PRO 10.0: COMMAND CENTER")
m = st.sidebar.radio("MENU:", ["📊 STATYSTYKI", "📦 MAGAZYN SKU", "⚙️ USTAWIENIA"])

if m == "📊 STATYSTYKI":
    if not df_p.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("ASORTYMENT (SKU)", len(df_p))
        c2.metric("SUMA SZTUK", int(df_p['liczba'].sum()))
        c3.metric("ŚR. JAKOŚĆ", f"{df_p['ocena'].mean():.1f}")
        
        st.subheader("STRUKTURA ZAPASÓW")
        # Naprawa błędu ValueError przez jawne ustawienie template
        f1 = px.pie(df_p, names='kat_n', values='liczba', hole=0.4)
        f1.update_layout(template="plotly_dark")
        st.plotly_chart(f1, use_container_width=True)
        
        st.subheader("ILOŚCI WG PRODUKTÓW")
        f2 = px.bar(df_p, x='nazwa', y='liczba', color='ocena')
        f2.update_layout(template="plotly_dark")
        st.plotly_chart(f2, use_container_width=True)
    else: st.info("Baza jest pusta. Dodaj towary!")

elif m == "📦 MAGAZYN SKU":
    t1, t2 = st.tabs(["🔍 EWIDENCJA",
