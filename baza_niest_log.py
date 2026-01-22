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

# --- STYLIZACJA CSS (NAPRAWIONA SKŁADNIA) ---
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), 
        url("https://images.unsplash.com/photo-1494412519320-aa613dfb7738?q=80&w=2070");
        background-attachment: fixed;
        background-size: cover;
    }

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

    html, body, [class*="st-"] {
        font-family: 'Segoe UI', sans-serif;
        color: #FFFFFF !important;
        line-height: 1.6;
    }

    h1, h2, h3 { 
        color: #00ff88 !important; 
        text-transform: uppercase;
    }

    [data-testid="stMetric"] {
        background: #111;
        border: 2px solid #00ff88;
        border-radius: 12px;
        padding: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- POŁĄCZENIE Z BAZĄ (NAPRAWIONY BLOK TRY/EXCEPT) ---
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
    st.success("POŁĄCZONO Z BAZĄ")

# --- MODUŁ 1: DASHBOARD (RAPORTY) ---
if menu == "📊 Dashboard":
    st.title("📊 Statystyki Magazynowe")
    if not df_prod.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Pozycje", len(df_prod))
        c2.metric("Suma Sztuk", int(df_prod['liczba'].sum()))
        c3.metric("Średnia Jakość", f"{df_prod['ocena'].mean():.2f}")

        st.divider()
        col_l, col_r = st.columns(2)
        with col_l:
            # Naprawione wywołanie wykresu (zamknięte nawiasy)
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

# --- MODUŁ 2: INWENTARZ (OBSŁUGA) ---
elif menu == "📦 Inwentarz":
    st.title("📦 Zarządzanie Towarem")
    t1, t2 = st.tabs(["🔍 Lista", "📥 Nowa Dostawa"])
    
    with t1:
        search = st.text_input("Szukaj produktu:")
        if not df_prod.empty:
            df_f = df_prod[df_prod['nazwa'].str.contains(search, case=False)]
            st.dataframe(df_f[['nazwa', 'kat_nazwa', 'liczba', 'ocena']], use_container_width=True, hide_index=True)
            
            with st.expander("🗑️ Usuwanie produktu"):
                target = st.selectbox("Wybierz do usunięcia:", df_prod['nazwa'].tolist())
                if st.button("POTWIERDŹ USUNIĘCIE", type="primary"):
                    id_to_del = df_prod[df_prod['nazwa'] == target]['id'].values[0]
                    supabase.table("produkty").delete().eq("id", id_to_del).execute()
                    st.cache_data.clear()
                    st.rerun()

    with t2:
        if not df_kat.empty:
            k_map = {r['nazwa']: r['id'] for _, r in df_kat.iterrows()}
            with st.form("dostawa_form"):
                ca, cb = st.columns(2)
                p_n = ca.text_input("Nazwa produktu")
                p_k = cb.selectbox("Kategoria", options=list(k_map.keys()))
                cc, cd = st.columns(2)
                p_q = cc.number_input("Ilość", min_value=1)
                p_o = cd.slider("Ocena jakości", 0.0, 5.0, 4.0)
                if st.form_submit_button("DODAJ PRODUKT", use_container_width=True):
                    if p_n:
                        supabase.table("produkty").insert({
                            "nazwa": p_n, "liczba": p_q, 
                            "ocena": p_o, "kategoria_id": k_map[p_k]
                        }).execute()
                        st.cache_data.clear()
                        st.rerun()
        else:
            st.warning("Najpierw dodaj kategorie w panelu Konfiguracja.")

# --- MODUŁ 3: KONFIGURACJA ---
elif menu == "⚙️ Konfiguracja":
    st.title("⚙️ Struktura Bazy")
    col1, col2 = st.columns([1, 2])
    with col1:
        with st.form("kat_form"):
            nk = st.text_input("Nowa Kategoria")
            ok = st.text_area("Opis")
            if st.form_submit_button("DODAJ"):
                if nk:
                    supabase.table("kategorie").insert({"nazwa": nk, "opis": ok}).execute()
                    st.cache_data.clear()
                    st.rerun()
    with col2:
        if not df_kat.empty:
            st.table(df_kat[['nazwa', 'opis']])
