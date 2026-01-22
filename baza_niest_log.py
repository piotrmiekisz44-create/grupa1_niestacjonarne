import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# --- 1. SETUP & STYLE ---
st.set_page_config(page_title="LOG-PRO 14.0", layout="wide")

st.markdown("""<style>
.stApp {background: linear-gradient(rgba(0,0,0,0.8),rgba(0,0,0,0.8)), url("https://images.unsplash.com/photo-1553413077-190dd305871c?w=1000"); background-size: cover;}
h1, h2, label, p, .stMetric {color: #00FFCC !important; font-weight: 800 !important; text-shadow: 1px 1px 2px #000;}
div.stButton > button {
    background: #FFD700 !important; color: #000 !important; font-size: 22px !important;
    font-weight: 900 !important; border: 3px solid #00FFCC !important;
    height: 70px !important; border-radius: 15px !important; box-shadow: 0 0 15px #00FFCC;
}
div.stButton > button:hover {background: #00FFCC !important; color: #000 !important; transform: scale(1.02);}
</style>""", unsafe_allow_html=True)

# --- 2. DATA CONNECTION ---
@st.cache_resource
def init():
    u, k = st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
    return create_client(u, k)

db = init()

def load():
    try:
        p = db.table("produkty").select("*, kategorie(nazwa)").execute()
        k = db.table("kategorie").select("*").execute()
        df = pd.DataFrame(p.data)
        if not df.empty:
            df['k'] = df['kategorie'].apply(lambda x: x['nazwa'] if isinstance(x, dict) else "Inne")
        return df, pd.DataFrame(k.data)
    except: return pd.DataFrame(), pd.DataFrame()

df_p, df_k = load()

# --- 3. NAVIGATION ---
m = st.sidebar.radio("MODUŁ OPERACYJNY", ["📊 STATUS", "📦 MAGAZYN", "📈 ANALIZA", "⚙️ USTAWIENIA"])

# --- MODUŁ: STATUS ---
if m == "📊 STATUS":
    st.title("🚀 DASHBOARD KPI")
    if not df_p.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("SKU", len(df_p))
        c2.metric("SZTUKI", int(df_p['liczba'].sum()))
        c3.metric("JAKOŚĆ", round(df_p['ocena'].mean(), 1))
        
        st.subheader("STRUKTURA ZAPASÓW")
        f1 = px.pie(df_p, names='k', values='liczba', hole=0.4)
        f1.update_layout(template="plotly_dark", margin=dict(t=0,b=0,l=0,r=0))
        st.plotly_chart(f1, use_container_width=True)
    else: st.info("Dodaj towary w sekcji Magazyn")

# --- MODUŁ: MAGAZYN ---
elif m == "📦 MAGAZYN":
    st.title("📦 KONTROLA SKU")
    t1, t2 = st.tabs(["🔍
