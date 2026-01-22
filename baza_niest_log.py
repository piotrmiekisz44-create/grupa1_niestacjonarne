import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# 1. Konfiguracja strony
st.set_page_config(page_title="LOG-PRO 6.0", layout="wide", page_icon="🚚")

# 2. DESIGN: Maksymalnie widoczne przyciski i czcionki
st.markdown("""
<style>
.stApp {
    background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), 
    url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070");
    background-attachment: fixed; background-size: cover;
}
/* Pogrubienie wszystkich tekstów */
label, p, .stMetric, .stSelectbox, .stSlider, h1, h2, h3 {
    color: #FFFFFF !important; font-weight: 900 !important; text-shadow: 2px 2px 4px #000000;
}
/* PRZYCISKI: Jaskrawy zielony, duży, pogrubiony */
div.stButton > button:first-child {
    background-color: #00FF00 !important; color: #000000 !important;
    font-size: 20px !important; font-weight: bold !important;
    border: 3px solid #FFFFFF !important; border-radius: 15px !important;
    height: 3em !important; transition: 0.3s;
}
div.stButton > button:first-child:hover {
    background-color: #FF00FF !important; color: #FFFFFF !important; transform: scale(1.02);
}
/* PRZYCISK USUWANIA: Jaskrawy czerwony */
.stButton button[kind="secondary"] {
    background-color: #FF0000 !important; color: white !important;
}
/* Formularze */
div[data-testid="stForm"] {
    background-color: rgba(255, 255, 255, 0.1);
    border: 4px solid #00FF00; border-radius: 20px; padding: 30px;
}
</style>
""", unsafe_allow_html=True)

# 3. Połączenie z Bazą
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
            df['kat_nazwa'] = df['kategorie'].apply(lambda x: x['nazwa'] if isinstance(x, dict) else "Inne")
        return df, pd.DataFrame(k.data)
    except:
        return pd.DataFrame(), pd.DataFrame()

df_p, df_k = load_data()

# 4. Główne Menu
st.title("🚢 LOG-PRO 6.0: Warehouse Control")
page = st.sidebar.radio("WYBIERZ MODUŁ:", ["📊 STATYSTYKI I WYKRESY", "📦 ZARZĄDZANIE ZASOBAMI", "⚙️ KONFIGURACJA"])

# --- MODUŁ 1: STATYSTYKI ---
if page == "📊 STATYSTYKI I WYKRESY":
    if not df_p.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("SKU (ASORTYMENT)", len(df_p))
        c2.metric("SUMA SZTUK", int(df_p['liczba'].sum()))
        c3.metric("ŚREDNIA OCENA", f"{df_p['ocena'].mean():.2f}")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Struktura Kategorii (Kołowy)")
            fig1 = px.pie(df_p, names='kat_nazwa', values='liczba', hole=0.4, template="dark")
            st.plotly_chart(fig1, use_container_width=True)
        with col_b:
            st.subheader("Ilość Towaru wg Grupy (Słupkowy)")
            fig2 = px.bar(df_p, x='kat_nazwa', y='liczba', color='ocena', template="dark")
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Baza jest pusta.")

# --- MODUŁ 2: ZASOBY ---
elif page == "📦 ZARZĄDZANIE ZASOBAMI":
    tab1, tab2 = st.tabs(["🔍 PODGLĄD I USUWANIE", "➕ NOWA DOSTAWA"])
    
    with tab1:
        if not df_p.empty:
            st.dataframe(df_p[['nazwa', 'kat_nazwa', 'liczba', 'ocena']], use_container_width=True)
            st.markdown("---")
            st.subheader("❌ STREFA USUWANIA")
            target = st.selectbox("Wybierz towar do wycofania:", df_p['nazwa'].tolist())
            if st.button("USUŃ WYBRANY TOWAR", kind="secondary"):
                tid = df_p[df_p['nazwa'] == target]['id'].values[0]
                db.table("produkty").delete().eq("id", tid).execute()
                st.rerun()
        
    with tab2:
        with st.form("dostawa_6"):
            st.write("### FORMULARZ PRZYJĘCIA TOWARU")
            n = st.text_input("NAZWA TOWARU")
            k = st.selectbox("
