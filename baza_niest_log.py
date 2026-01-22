import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

# 1. Konfiguracja strony - Tryb szeroki dla lepszej czytelności
st.set_page_config(
    page_title="LOG-MASTER: System Zarządzania Transportem", 
    page_icon="🚛", 
    layout="wide"
)

# --- WYRAŹNE TŁO I WYSOKI KONTRAST (CSS) ---
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
        url("https://images.unsplash.com/photo-1494412519320-aa613dfb7738?q=80&w=2070");
        background-attachment: fixed;
        background-size: cover;
    }
    /* Kontener treści - maksymalny kontrast */
    .main .block-container {
        background-color: rgba(0, 0, 0, 0.85);
        padding: 40px;
        border-radius: 15px;
        border: 2px solid #00d4ff;
    }
    /* Stylizacja metryk (KPI) */
    [data-testid="stMetric"] {
        background: #0e1117;
        border: 1px solid #00ff88;
        border-radius: 10px;
        padding: 15px;
    }
    h1, h2, h3 { color: #00ff88 !important; text-transform: uppercase; }
    p, span, label { color: #ffffff !important; font-weight: 500; }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicjalizacja bazy danych Supabase
@st.cache_resource
def init_db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_db()

# 3. Pobieranie danych z obsługą błędów
@st.cache_data(ttl=5)
def load_data():
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

df_prod, df_kat = load_data()

# --- SIDEBAR: NAWIGACJA ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🚢 LOG-PRO OS</h1>", unsafe_allow_html=True)
    st.divider()
    menu = st.radio(
        "WYBIERZ MODUŁ:", 
        ["📊 Centrum Statystyk", "📦 Ewidencja Towarów", "🛠️ Konfiguracja Grup"],
        help="Nawiguj między podglądem danych a ich edycją."
    )
    st.divider()
    st.success("STATUS: SYSTEM POŁĄCZONY")

# --- MODUŁ 1: DASHBOARD ---
if menu == "📊 Centrum Statystyk":
    st.title("📊 Analityka Magazynowa")
    st.markdown("W tej sekcji zobaczysz aktualny stan całego centrum logistycznego.")
    
    if not df_prod.empty:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Pozycje", len(df_prod), help="Całkowita liczba unikalnych produktów.")
        c2.metric("Suma sztuk", int(df_prod['liczba'].sum()), help="Łączna ilość towaru.")
        c3.metric("Średnia Jakość", f"{df_prod['ocena'].mean():.2f} ⭐")
        
        low_stock = len(df_prod[df_prod['liczba'] < 5])
        c4.metric("Braki (stan < 5)", low_stock, delta=f"-{low_stock}", delta_color="inverse")

        st.divider()
        col_l, col_r = st.columns(2)
        
        with col_l:
            st.subheader("📦 Ilość towaru wg kategorii")
            fig1 = px.bar(
                df_prod.groupby('kat_nazwa')['liczba'].sum().reset_index(), 
                x='kat_nazwa', y='liczba', color='liczba',
                labels={'kat_nazwa':'Kategoria', 'liczba':'Sztuki'},
                template="plotly_dark", color_continuous_scale='Turbo'
            )
            st.plotly_chart(fig1, use_container_width=True)
            
        with col_r:
            st.subheader("🗺️ Udział procentowy zapasów")
            fig2 = px.pie(
                df_prod, names='kat_nazwa', values='liczba', hole=0.6,
                template="plotly_dark"
            )
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("System czeka na dane. Dodaj produkty w zakładce Ewidencja.")

# --- MODUŁ 2: EWIDENCJA ---
elif menu == "📦 Ewidencja Towarów":
    st.title("📦 Panel Operacyjny")
    t1, t2 = st.tabs(["🔍 Przegląd i Filtrowanie", "📥 Przyjęcie Dostawy"])
    
    with t1:
        st.subheader("Lista aktywnych zapasów")
        st.markdown("_Poniższa tabela przedstawia aktualne stany. Możesz użyć wyszukiwarki._")
        search = st.text_input("Szukaj produktu po nazwie:", placeholder="Np. Kontener...")
        
        if not df_prod.empty:
            df_filtered = df_prod[df_prod['nazwa'].str.contains(search, case=False)]
            # Zmiana nazw kolumn dla laika
            df_v = df_filtered[['nazwa', 'kat_nazwa', 'liczba', 'ocena']].copy()
            df_v.columns = ['Nazwa Produktu', 'Kategoria', 'Ilość w magazynie', 'Ocena Jakości']
            st.dataframe(df_v, use_container_width=True, hide_index=True)
            
            with st.expander("🗑️ Usuwanie produktu (Procedura zwrotu)"):
                st.warning("Uwaga: Usunięcie jest trwałe!")
                target = st.selectbox("Wybierz towar do usunięcia:", df_prod['nazwa'].tolist())
                if st.button("🔴 POTWIERDŹ USUNIĘCIE", type="primary"):
                    id_to_del = df_prod[df_prod['nazwa'] == target]['id'].values[0]
                    supabase.table("produkty").delete().eq("id", id_to_del).execute()
                    st.cache_data.clear()
                    st.rerun()

    with t2:
        st.subheader("Formularz nowej dostawy")
        st.markdown("Użyj tego formularza, aby wprowadzić nowy towar do systemu.")
        if not df_kat.empty:
            k_map = {row['nazwa']: row['id'] for _, row in df_kat.iterrows()}
            with st.form("dostawa_form", clear_on_submit=True):
                ca, cb = st.columns(2)
                nazwa_p = ca.text_input("Nazwa handlowa produktu", help="Np. Opony ciężarowe X-200")
                kat_p = cb.selectbox("Kategoria logistyczna", options=list(k_map.keys()), help="Do której grupy przypisać towar?")
                
                cc, cd = st.columns(2)
                ilo_p = cc.number_input("Ilość dostarczonych sztuk", min_value=1, value=10)
                ocen_p = cd.slider("Ocena jakości partii (0-5)", 0.0, 5.0, 4.0)
                
                if st.form_submit_button("✅ ZATWIERDŹ PRZYJĘCIE", use_container_width=True):
                    if nazwa_p:
                        supabase.table("produkty").insert({
                            "nazwa": nazwa_p, "liczba": ilo_p, 
                            "ocena": ocen_p, "kategoria_id": k_map[kat_p]
                        }).execute()
                        st.cache_data.clear()
                        st.success("Towar pomyślnie dodany do bazy danych!")
                        st.rerun()
        else:
            st.error("Błąd: Musisz najpierw dodać kategorie w zakładce 'Konfiguracja Grup'!")

# --- MODUŁ 3: KONFIGURACJA ---
elif menu == "🛠️ Konfiguracja Grup":
    st.title("🛠️ Zarządzanie Architekturą Magazynu")
    st.markdown("W tej sekcji zarządzasz kategoriami (grupami), do których przypisujesz towary.")
    
    cola, colb = st.columns([1, 2])
    
    with cola:
        st.subheader("Dodaj nową grupę")
        with st.form("kat_form"):
            nk = st.text_input("Nazwa nowej kategorii", help="Np. Materiały niebezpieczne, Elektronika")
            ok = st.text_area("Krótki opis operacyjny")
            if st.form_submit_button("DODAJ KATEGORIĘ"):
                if nk:
                    supabase.table("kategorie").insert({"nazwa": nk, "opis": ok}).execute()
                    st.cache_data.clear()
                    st.rerun()

    with colb:
        st.subheader("Aktualnie zdefiniowane kategorie")
        if not df_kat.empty:
            st.table(df_kat[['nazwa', 'opis']])
