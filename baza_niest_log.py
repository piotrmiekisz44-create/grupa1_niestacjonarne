import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="LOG-PRO 7.0", layout="wide")

# STYLIZACJA I TŁO
st.markdown("""
<style>
.stApp { background-image: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070"); background-size: cover; }
label, p, .stMetric { color: white !important; font-weight: bold !important; font-size: 1.2rem; }
.stButton>button { background-color: #00FF00 !important; color: black !important; font-weight: bold; width: 100%; border-radius: 10px; border: 2px solid white; }
</style>
""", unsafe_allow_html=True)

# POŁĄCZENIE
@st.cache_resource
def init():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

db = init()

# DANE
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

# MENU
st.title("🚢 LOG-PRO 7.0")
m = st.sidebar.radio("NAWIGACJA", ["DASHBOARD", "MAGAZYN", "SYSTEM"])

if m == "DASHBOARD":
    if not df_p.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("SKU", len(df_p))
        c2.metric("SZTUK", int(df_p['liczba'].sum()))
        c3.metric("OCENA", f"{df_p['ocena'].mean():.1f}")
        
        st.plotly_chart(px.pie(df_p, names='kat', values='liczba', hole=0.4, template="dark"), use_container_width=True)
        st.plotly_chart(px.bar(df_
