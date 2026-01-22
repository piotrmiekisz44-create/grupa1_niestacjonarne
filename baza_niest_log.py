import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# 1. Konfiguracja strony
st.set_page_config(page_title="LOG-PRO 5.0", layout="wide", page_icon="🚚")

# 2. Wyraźny Design (Białe, pogrubione czcionki i czytelne przyciski)
st.markdown("""
<style>
.stApp {
    background-image: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), 
    url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070");
    background-attachment: fixed; background-size: cover;
}
label, p, .stMetric, .stSelectbox, .stSlider {
    color: white !important; font-weight: bold !important; font-size: 1.1rem !important;
}
.stButton>button {
    border-radius: 10px; border: 2px solid #4CAF50;
    background-color: #1b5e20; color: white !important;
    font-weight: bold !important; width: 100%;
}
div[data-testid="stForm"] {
    background-color: rgba(0, 0, 0, 0.7);
    border: 2px solid #2e7d32; border-radius: 15px; padding: 20px;
}
</style>
""", unsafe_allow_html=True)

# 3. Połączenie i Dane
@st.cache_resource
def init_db():
    u = st.secrets["SUPABASE_URL"]
    k = st.secrets["SUPABASE_KEY"]
    return create_client(u, k)

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

# 4. Menu Główne
st.title("🚢 LOG-PRO: Global Logistic Command Center")
page = st.sidebar.radio("MODUŁY SYSTEMU:", ["📊 Dashboard", "📦 Magazyn SKU", "📑 Raporty CSV", "⚙️ Ustawienia"])

# --- MODUŁ 1: DASHBOARD ---
if page == "📊 Dashboard":
    if not df_p.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("SKU W BAZIE", len(df_p))
        c2.metric("SUMA ZAPASÓW", int(df_p['liczba'].sum()))
        c3.metric("ŚR. JAKOŚĆ", f"{df_p['ocena'].mean():.1f}/5")
        
        fig = px.pie(df_p, names='kat_nazwa', values='liczba', hole=0.4, template="dark")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Baza jest pusta. Dodaj towary w sekcji Magazyn.")

# --- MODUŁ 2: MAGAZYN SKU ---
elif page == "📦 Magazyn SKU":
    t1, t2 = st.tabs(["🔍 PODGLĄD STANU", "➕ NOWA DOSTAWA"])
    
    with t1:
        if not df_p.empty:
            st.dataframe(df_p[['nazwa', 'kat_nazwa', 'liczba', 'ocena']], use_container_width=True)
            if st.button("USUŃ OSTATNIO DODANY PRODUKT"):
                db.table("produkty").delete().eq("id", df_p.iloc[-1]['id']).execute()
                st.rerun()
        
    with t2:
        with st.form("fm_add"):
            st.write("WPROWADŹ DANE DOSTAWY")
            n = st.text_input("NAZWA TOWARU")
            k = st.selectbox("GRUPA LOGISTYCZNA", df_k['nazwa'].tolist() if not df_k.empty else ["Brak"])
            l = st.number_input("ILOŚĆ SZTUK", min_value=1)
            o = st.slider("OCENA TECHNICZNA", 1, 5, 4)
            if st.form_submit_button("ZATWIERDŹ PRZYJĘCIE"):
                kid = df_k[df_k['nazwa'] == k]['id'].values[0]
                db.table("produkty").insert({"nazwa": n, "kategoria_id": kid, "liczba": l, "ocena": o}).execute()
                st.rerun()

# --- MODUŁ 3: RAPORTY ---
elif page == "📑 Raporty CSV":
    st.subheader("Eksport danych magazynowych")
    if not df_p.empty:
        f_kat = st.multiselect("Filtruj grupy:", df_p['kat_nazwa'].unique())
        df_f = df_p[df_p['kat_nazwa'].isin(f_kat)] if f_kat else df_p
        st.dataframe(df_f, use_container_width=True)
        st.download_button("POBIERZ PLIK CSV", df_f.to_csv(index=False), "log_pro_export.csv")

# --- MODUŁ 4: USTAWIENIA ---
elif page == "⚙️ Ustawienia":
    st.subheader("Konfiguracja Kategorii")
    with st.form("fm_sys"):
        new_c = st.text_input("Nazwa nowej grupy logistycznej")
        if st.form_submit_button("UTWÓRZ KATEGORIĘ"):
            db.table("kategorie").insert({"nazwa": new_c}).execute()
            st.rerun()
