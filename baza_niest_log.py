import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

# --- KONFIGURACJA WIZUALNA ---
st.set_page_config(page_title="Warehouse Intel OS", page_icon="🕋", layout="wide")

# Zaawansowana stylizacja CSS (Ciemny motyw magazynu)
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), 
        url("https://images.unsplash.com/photo-1587293855946-b52c974416ae?q=80&w=2070");
        background-attachment: fixed;
        background-size: cover;
    }
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 15px;
        padding: 15px;
    }
    h1, h2, h3 { color: #00d4ff !important; text-shadow: 2px 2px 5px #000; }
    </style>
    """, unsafe_allow_html=True)

# Połączenie z Supabase
@st.cache_resource
def init_db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_db()

# Pobieranie danych
@st.cache_data(ttl=5)
def get_warehouse_data():
    try:
        # Relacja produktów i kategorii
        p_res = supabase.table("produkty").select("*, kategorie(nazwa)").execute()
        k_res = supabase.table("kategorie").select("*").execute()
        df_p = pd.DataFrame(p_res.data)
        df_k = pd.DataFrame(k_res.data)
        if not df_p.empty and 'kategorie' in df_p.columns:
            df_p['kat_nazwa'] = df_p['kategorie'].apply(lambda x: x['nazwa'] if isinstance(x, dict) else "Brak")
        return df_p, df_k
    except:
        return pd.DataFrame(), pd.DataFrame()

df_prod, df_kat = get_warehouse_data()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🕋 WI-OS v4.2</h1>", unsafe_allow_html=True)
    menu = st.radio("MODUŁY:", ["📊 Dashboard", "📦 Inwentarz", "📈 Predykcja", "⚙️ Baza"])
    st.divider()
    st.success("POŁĄCZENIE AKTYWNE")

# --- MODUŁY ---
if menu == "📊 Dashboard":
    st.title("📊 Warehouse Real-time Dashboard")
    if not df_prod.empty:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Asortyment", len(df_prod))
        c2.metric("Suma Zapasu", int(df_prod['liczba'].sum()))
        c3.metric("Średnia Jakość", f"{df_prod['ocena'].mean():.2f}")
        low = len(df_prod[df_prod['liczba'] < 5])
        c4.metric("Krytyczne Braki", low, delta=f"-{low}", delta_color="inverse")

        col_l, col_r = st.columns(2)
        with col_l:
            fig1 = px.bar(df_prod.groupby('kat_nazwa')['liczba'].sum().reset_index(), 
                         x='kat_nazwa', y='liczba', color='liczba',
                         title="Stany wg Kategorii", template="plotly_dark",
                         color_continuous_scale='Blues')
            st.plotly_chart(fig1, use_container_width=True)
        with col_r:
            fig2 = px.pie(df_prod, names='kat_nazwa', values='liczba', hole=0.5,
                         title="Udział Kategorii", template="plotly_dark")
            st.plotly_chart(fig2, use_container_width=True)

elif menu == "📦 Inwentarz":
    st.title("📦 Kontrola i Ewidencja")
    t1, t2 = st.tabs(["📋 Lista Produktów", "📥 Nowa Dostawa"])
    with t1:
        search = st.text_input("Szukaj produktu...")
        if not df_prod.empty:
            df_f = df_prod[df_prod['nazwa'].str.contains(search, case=False)]
            st.dataframe(df_f[['nazwa', 'kat_nazwa', 'liczba', 'ocena']], 
                         use_container_width=True, hide_index=True)
            with st.expander("Usuń produkt"):
                target = st.selectbox("Wybierz pozycję", df_prod['nazwa'].tolist())
                if st.button("USUŃ Z BAZY", type="primary"):
                    id_d = df_prod[df_prod['nazwa'] == target]['id'].values[0]
                    supabase.table("produkty").delete().eq("id", id_d).execute()
                    st.cache_data.clear()
                    st.rerun()
    with t2:
        if not df_kat.empty:
            k_map = {r['nazwa']: r['id'] for _, r in df_kat.iterrows()}
            with st.form("add_p", clear_on_submit=True):
                ca, cb = st.columns(2)
                n = ca.text_input("Nazwa")
                k = cb.selectbox("Kategoria", options=list(k_map.keys()))
                l = st.number_input("Ilość", min_value=0)
                o = st.slider("Ocena", 0.0, 5.0, 4.0)
                if st.form_submit_button("WPROWADŹ", use_container_width=True):
                    supabase.table("produkty").insert({"nazwa": n, "liczba": l, "ocena": o, "kategoria_id": k_map[k]}).execute()
                    st.cache_data.clear()
                    st.rerun()

elif menu == "📈 Predykcja":
    st.title("📈 Analiza Jakościowa")
    if not df_prod.empty:
        fig3 = px.scatter(df_prod, x="liczba", y="ocena", color="kat_nazwa", 
                         size="liczba", hover_name="nazwa", template="plotly_dark",
                         title="Mapa: Ilość vs Jakość")
        st.plotly_chart(fig3, use_container_width=True)

elif menu == "⚙️ Baza":
    st.title("⚙️ Architektura Bazy")
    col1, col2 = st.columns([1, 2])
    with col1:
        with st.form("add_k"):
            nk = st.text_input("Nowa Kategoria")
            ok = st.text_area("Opis")
            if st.form_submit_button("DODAJ GRUPĘ"):
                if nk:
                    supabase.table("kategorie").insert({"nazwa": nk, "opis": ok}).execute()
                    st.cache_data.clear()
                    st.rerun()
    with col2:
        st.table(df_kat[['nazwa', 'opis']])
