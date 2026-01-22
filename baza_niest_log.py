import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# 1. Konfiguracja i Stylizacja
st.set_page_config(page_title="LOG-PRO 5.0", layout="wide", page_icon="🚚")

def apply_ui():
    st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
        url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070");
        background-attachment: fixed; background-size: cover;
    }
    label, p, .stMetric, .stSelectbox {
        color: white !important; font-weight: bold !important;
    }
    .stButton>button {
        border-radius: 10px; border: 2px solid #4CAF50;
        background-color: #1b5e20; color: white !important; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

apply_ui()

# 2. Baza danych
@st.cache_resource
def init_db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

db = init_db()

def get_data():
    try:
        p = db.table("produkty").select("*, kategorie(nazwa)").execute()
        k = db.table("kategorie").select("*").execute()
        df = pd.DataFrame(p.data)
        if not df.empty:
            df['kat_nazwa'] = df['kategorie'].apply(lambda x: x['nazwa'] if isinstance(x, dict) else "Inne")
        return df, pd.DataFrame(k.data)
    except:
        return pd.DataFrame(), pd.DataFrame()

df_p, df_k = get_data()

# 3. Nawigacja
st.title("🚢 LOG-PRO: Logistic Command Center")
page = st.sidebar.radio("MODUŁY:", ["📊 Dashboard", "📦 Magazyn", "📑 Raporty", "⚙️ System"])

# --- DASHBOARD ---
if page == "📊 Dashboard":
    if not df_p.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("ASORTYMENT", len(df_p))
        c2.metric("SUMA ZAPASÓW", int(df_p['liczba'].sum()))
        c3.metric("ŚR. JAKOŚĆ", f"{df_p['ocena'].mean():.1f}/5")
        fig = px.pie(df_p, names='kat_nazwa', values='liczba', template="dark", hole=0.3)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Brak danych.")

# --- MAGAZYN ---
elif page == "📦 Magazyn":
    t1, t2 = st.tabs(["🔍 LISTA SKU", "➕ NOWA DOSTAWA"])
    with t1:
        if not df_p.empty:
            st.dataframe(df_p[['nazwa', 'kat_nazwa', 'liczba', 'ocena']], use_container_width=True)
            if st.button("USUŃ PIERWSZY REKORD"):
                db.table("produkty").delete().eq("id", df_p.iloc[0]['id']).execute()
                st.rerun()
    with t2:
        with st.form("dostawa_form"):
            nazwa = st.text_input("Nazwa towaru")
            kat_n = st.selectbox("Grupa", df_k['nazwa'].tolist() if not df_k.empty else ["Brak"])
            ilosc = st.number_input("Ilość", min_value=1)
            ocena = st.slider("J
