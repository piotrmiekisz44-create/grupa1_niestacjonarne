import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# 1. KONFIGURACJA I STYLIZACJA
st.set_page_config(page_title="LOG-PRO 13.0", layout="wide", page_icon="🏢")

st.markdown("""<style>
.stApp {background: linear-gradient(rgba(0,0,0,0.85),rgba(0,0,0,0.85)), url("https://images.unsplash.com/photo-1553413077-190dd305871c?q=80&w=2000"); background-size: cover;}
h1, h2, label, p, .stMetric {color: #00FFCC !important; font-weight: 800 !important; text-shadow: 1px 1px 3px #000;}
div.stButton > button {
    background: #FFD700 !important; color: #000 !important; font-size: 20px !important;
    font-weight: 800 !important; border: 3px solid #00FFCC !important;
    height: 60px !important; width: 100% !important; border-radius: 12px !important;
    box-shadow: 0 4px 15px rgba(0,255,204,0.3);
}
div.stButton > button:hover {background: #00FFCC !important; transform: translateY(-2px);}
.stTabs [data-baseweb="tab-list"] {gap: 20px;}
.stTabs [data-baseweb="tab"] {
    background-color: rgba(255,255,255,0.1); border-radius: 10px 10px 0 0;
    padding: 10px 20px; color: white !important;
}
</style>""", unsafe_allow_html=True)

# 2. POŁĄCZENIE
@st.cache_resource
def init_db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

db = init_db()

def load_data():
    try:
        p = db.table("produkty").select("*, kategorie(nazwa)").execute()
        k = db.table("kategorie").select("*").execute()
        df = pd.DataFrame(p.data)
        if not df.empty:
            df['kat_n'] = df['kategorie'].apply(lambda x: x['nazwa'] if isinstance(x, dict) else "Inne")
        return df, pd.DataFrame(k.data)
    except: return pd.DataFrame(), pd.DataFrame()

df_p, df_k = load_data()

# 3. PASEK BOCZNY (NAWIGACJA)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2312/2312677.png", width=100)
    st.title("GŁÓWNE MENU")
    menu = st.radio("Wybierz moduł operacyjny:", 
                    ["📊 Dashboard KPI", "📦 Magazyn & Dostawy", "
