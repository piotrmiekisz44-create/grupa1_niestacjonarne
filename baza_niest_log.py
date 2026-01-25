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

# --- STYLIZACJA CSS (ZAKCENTOWANE POLA TEKSTOWE) ---
st.markdown("""
    <style>
    /* Tło i główny kontener */
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), 
        url("https://images.unsplash.com/photo-1494412519320-aa613dfb7738?q=80&w=2070");
        background-attachment: fixed;
        background-size: cover;
    }

    /* Panele i kontenery */
    [data-testid="stSidebar"] {
        background-color: #050505 !important;
        border-right: 2px solid #00ff88;
    }
    
    .main .block-container {
        background-color: rgba(0, 0, 0, 0.92);
        padding: 40px;
        border-radius: 20px;
        border: 1px solid rgba(0, 212, 255, 0.3);
    }

    /* Teksty ogólne */
    html, body, [class*="st-"] {
        font-family: 'Segoe UI', sans-serif;
        color: #FFFFFF !important;
    }

    h1, h2, h3 { 
        color: #00ff88 !important; 
        text-transform: uppercase;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }

    /* KLUCZOWE: Stylizacja pól tekstowych i liczbowych */
    input, textarea, select, div[data-baseweb="select"] > div {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border: 2px solid #00ff88 !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        font-size: 16px !important;
    }

    /* Stylizacja etykiet nad polami (Label) */
    .stMarkdown p, label {
        color: #00ff88 !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }

    /* Fokus na polach (po kliknięciu) */
    input:focus, textarea:focus {
        border-color: #00d4ff !important;
        box-shadow: 0 0 10px #00d4ff !important;
    }

    /* Metryki */
    [data-testid="stMetric"] {
        background: #111;
        border: 2px solid #00ff88;
        border-radius: 12px;
        padding: 15px;
    }

    /* Przyciski */
    .stButton>button {
        background-color: #00ff88 !important;
        color: #000000 !important;
        font-weight: 900 !important;
        border-radius: 10px !important;
        border: none !important;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #00d4ff !important;
        transform: scale(1.02);
    }
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
    if not supabase: 
        return pd.DataFrame(), pd.DataFrame()
    try:
        p_res = supabase.table("produkty").select("*, kategorie(nazwa)").execute()
        k_res = supabase.table("kategorie").select("*").execute()
        df_p = pd.DataFrame(p_res.data)
        df_k = pd.DataFrame(k_res.data)
        
        if not df_p.empty and 'kategorie' in df_p.columns:
            df_p['kat_nazwa'] = df_p['kategorie'].apply(
                lambda x: x['nazwa'] if isinstance(x, dict) else "Brak"
            )
        return df_p, df_k
    except Exception:
        return pd.DataFrame(), pd.DataFrame()

df_prod, df_kat = get_data()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🚢 LOG-PRO</h1>", unsafe_allow_html=True)
    menu = st.radio(
        "WYBIERZ MODUŁ:", 
        ["📊 Dashboard", "📦 Inwentarz", "⚙️ Konfiguracja"]
    )
    st.divider()
    st.success("STATUS: POŁĄCZONO")

# --- MODUŁ 1: DASHBOARD ---
if menu == "📊 Dashboard":
    st.title("📊 Statystyki Magazynowe")
    if not df_prod.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Pozycje (SKU)", len(df_prod))
        c2.metric("Suma Sztuk", int(df_prod['liczba'].sum()))
        c3.metric("Średnia Jakość", f"{df_prod['ocena'].mean():.2f}")

        st.divider()
        col_l, col_r = st.columns(2)
        with col_l:
            fig1 = px.bar(
                df_prod.groupby('kat_nazwa')['liczba'].sum().reset_index(), 
                x='kat_nazwa', y='liczba', color='liczba',
                template="plotly_dark", title="Stany wg Kategorii"
            )
            st.plotly_chart(fig1, use_container_width=True)
        with col_r:
            fig2 = px.pie(
                df_prod, names='kat_nazwa', values='liczba', hole=0.5,
                template="plotly_dark", title="Udział w Inwentarzu"
            )
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Baza danych jest pusta.")

# --- MODUŁ 2: INWENTARZ ---
elif menu == "📦 Inwentarz":
    st.title("📦 Zarządzanie Towarem")
    t1, t2 = st.tabs(["🔍 Lista i Wyszukiwanie", "📥 Przyjęcie Nowej Dostawy"])
    
    with t1:
        search = st.text_input("Wpisz nazwę produktu, aby przefiltrować listę:")
        if not df_prod.empty:
            df_f = df_prod[df_prod['nazwa'].str.contains(search, case=False)]
            st.dataframe(df_f[['nazwa', 'kat_nazwa', 'liczba', 'ocena']], use_container_width=True, hide_index=True)
            
            with st.expander("🗑️ Procedura usuwania produktu"):
                target = st.selectbox("Wybierz artykuł do usunięcia z ewidencji:", df_prod['nazwa'].tolist())
                if st.button("DEFINITYWNIE USUŃ", type="primary", use_container_width=True):
                    id_to_del = df_prod[df_prod['nazwa'] == target]['id'].values[0]
                    supabase.table("produkty").delete().eq("id", id_to_del).execute()
                    st.cache_data.clear()
                    st.rerun()

    with t2:
        if not df_kat.empty:
            k_map = {r['nazwa']: r['id'] for _, r in df_kat.iterrows()}
            with st.form("dostawa_form"):
                ca, cb = st.columns(2)
                p_n = ca.text_input("Dokładna nazwa produktu")
                p_k = cb.selectbox("Przypisana kategoria", options=list(k_map.keys()))
                cc, cd = st.columns(2)
                p_q = cc.number_input("Ilość przyjmowanych jednostek", min_value=1)
                p_o = cd.slider("Ocena jakości towaru (0-5)", 0.0, 5.0, 4.0)
                if st.form_submit_button("ZATWIERDŹ PRZYJĘCIE TOWARU", use_container_width=True):
                    if p_n:
                        supabase.table("produkty").insert({
                            "nazwa": p_n, "liczba": p_q, 
                            "ocena": p_o, "kategoria_id": k_map[p_k]
                        }).execute()
                        st.cache_data.clear()
                        st.rerun()
        else:
            st.warning("Błąd: System nie wykrył żadnych kategorii. Dodaj je w module Konfiguracja.")

# --- MODUŁ 3: KONFIGURACJA ---
elif menu == "⚙️ Konfiguracja":
    st.title("⚙️ Ustawienia Struktury")
    col1, col2 = st.columns([1, 2])
    with col1:
        with st.form("kat_form"):
            st.write("Definiowanie nowej grupy towarowej")
            nk = st.text_input("Nazwa kategorii (np. Elektronika)")
            ok = st.text_area("Szczegółowy opis grupy")
            if st.form_submit_button("DODAJ GRUPĘ DO SYSTEMU"):
                if nk:
                    supabase.table("kategorie").insert({"nazwa": nk, "opis": ok}).execute()
                    st.cache_data.clear()
                    st.rerun()
    with col2:
        st.write("Istniejące kategorie w systemie:")
        if not df_kat.empty:
            st.table(df_kat[['nazwa', 'opis']])
