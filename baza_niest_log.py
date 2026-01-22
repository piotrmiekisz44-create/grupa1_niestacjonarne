import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

# --- KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="LOG-PRO: System Logistyczny", 
    page_icon="🚢", 
    layout="wide"
)

# --- STYLIZACJA CSS (WYSOKI KONTRAST) ---
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), 
        url("https://images.unsplash.com/photo-1494412519320-aa613dfb7738?q=80&w=2070");
        background-attachment: fixed;
        background-size: cover;
    }
    /* Panel główny */
    .main .block-container {
        background-color: rgba(20, 20, 20, 0.95);
        padding: 40px;
        border-radius: 15px;
        border: 1px solid #00ff88;
    }
    /* WYSOKI KONTRAST DLA PÓL TEKSTOWYCH */
    input, select, textarea, .stSelectbox, .stNumberInput, .stTextInput {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    div[data-baseweb="input"] input, div[data-baseweb="select"] {
        color: #000000 !important;
        background-color: #FFFFFF !important;
    }
    /* Etykiety i teksty */
    label, .stMarkdown p {
        color: #00d4ff !important;
        font-weight: 700 !important;
    }
    /* Tabele - czarny tekst na białym tle */
    .stDataFrame, [data-testid="stTable"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 10px;
    }
    /* Nagłówki */
    h1, h2, h3 { color: #00ff88 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- POŁĄCZENIE Z BAZĄ ---
@st.cache_resource
def init_db():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Błąd połączenia: {e}")
        return None

supabase = init_db()

# --- POBIERANIE DANYCH ---
@st.cache_data(ttl=5)
def get_data():
    if not supabase: return pd.DataFrame(), pd.DataFrame()
    try:
        p_res = supabase.table("produkty").select("*, kategorie(nazwa)").execute()
        k_res = supabase.table("kategorie").select("*").execute()
        df_p = pd.DataFrame(p_res.data)
        df_k = pd.DataFrame(k_res.data)
        if not df_p.empty and 'kategorie' in df_p.columns:
            df_p['kat_nazwa'] = df_p['kategorie'].apply(lambda x: x['nazwa'] if isinstance(x, dict) else "Brak")
        return df_p, df_k
    except:
        return pd.DataFrame(), pd.DataFrame()

df_prod, df_kat = get_data()

# --- INTERFEJS ---
with st.sidebar:
    st.title("🚢 LOG-PRO")
    menu = st.radio("MENU:", ["📊 Raporty", "📦 Magazyn", "⚙️ Ustawienia"])

if menu == "📊 Raporty":
    st.header("Analityka Magazynowa")
    if not df_prod.empty:
        col1, col2 = st.columns(2)
        with col1:
            fig1 = px.bar(df_prod.groupby('kat_nazwa')['liczba'].sum().reset_index(), 
                         x='kat_nazwa', y='liczba', title="Stan wg Kategorii")
            st.plotly_chart(fig1, use_container_width=True)
        with col2:
            fig2 = px.pie(df_prod, names='kat_nazwa', values='liczba', hole=0.4, title="Udział")
            st.plotly_chart(fig2, use_container_width=True)

elif menu == "📦 Magazyn":
    st.header("Zarządzanie Towarem")
    if not df_prod.empty:
        # Tabela z wysokim kontrastem (czarny tekst na białym tle)
        st.dataframe(df_prod[['nazwa', 'kat_nazwa', 'liczba', 'ocena']], use_container_width=True)
        
        with st.form("dodaj_towar"):
            st.subheader("Nowa Dostawa")
            nazwa = st.text_input("Nazwa produktu")
            ilosc = st.number_input("Ilość", min_value=1)
            if st.form_submit_button("DODAJ"):
                st.success(f"Dodano: {nazwa}")
                
