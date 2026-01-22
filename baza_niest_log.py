import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

# --- 1. KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="LOG-PRO: System Logistyczny", 
    page_icon="🚢", 
    layout="wide"
)

# --- 2. STYLIZACJA (CIEMNY SIDEBAR I CZYTELNOŚĆ) ---
st.markdown("""
    <style>
    /* Główne tło aplikacji */
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), 
        url("https://images.unsplash.com/photo-1494412519320-aa613dfb7738?q=80&w=2070");
        background-attachment: fixed;
        background-size: cover;
    }

    /* PASEK MENU (SIDEBAR) - Ciemniejszy, głęboki kolor */
    [data-testid="stSidebar"] {
        background-color: #050505 !important;
        border-right: 2px solid #00ff88;
    }
    
    /* PANEL GŁÓWNY - Bardziej kryjące tło dla lepszej czytelności tekstu */
    .main .block-container {
        background-color: rgba(0, 0, 0, 0.92);
        padding: 40px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-top: 20px;
    }

    /* CZYTELNOŚĆ CZCIONEK I TEKSTU */
    html, body, [class*="st-"] {
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        color: #FFFFFF !important;
        font-size: 1.05rem;
        line-height: 1.7; /* Większy odstęp między liniami dla przejrzystości */
    }

    /* Wyraźne nagłówki */
    h1, h2, h3 { 
        color: #00ff88 !important; 
        font-weight: 800 !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 15px !important;
    }

    /* Wyraźne etykiety formularzy i opisów */
    .stTextInput label, .stSelectbox label, .stNumberInput label, .stSlider label {
        color: #00d4ff !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        padding-bottom: 5px;
    }

    /* Stylizacja tabel i dataframe dla czytelności */
    .stDataFrame {
        border: 1px solid #333;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. POŁĄCZENIE Z BAZĄ ---
@st.cache_resource
def init_db():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Problem z połączeniem bazy: {e}")
        return None

supabase = init_db()

# --- 4. POBIERANIE DANYCH ---
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

# --- 5. MENU BOCZNE ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #00ff88;'>🚢 LOG-PRO</h1>", unsafe_allow_html=True)
    st.divider()
    # Naprawa nazw modułów dla większej czytelności
    menu = st.radio(
        "WYBIERZ MODUŁ:", 
        ["📊 Raporty Magazynowe", "📦 Obsługa Inwentarza", "⚙️ Konfiguracja Systemu"]
    )
    st.divider()
    st.success("POŁĄCZONO Z CHMURĄ")

# --- 6. MODUŁ 1: RAPORTY ---
if menu == "📊 Raporty Magazynowe":
    st.title("📊 Terminal Analityczny")
    st.markdown("Poniżej znajdują się kluczowe wskaźniki zapasów w czasie rzeczywistym.")
    
    if not df_prod.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Liczba pozycji", len(df_prod))
        c2.metric("Suma sztuk", int(df_prod['liczba'].sum()))
        c3.metric("Średnia jakość", f"{df_prod['ocena'].mean():.2f}")

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
        st.info("Brak danych do wyświetlenia. Dodaj produkty w panelu Obsługi.")

# --- 7. MODUŁ 2: OBSŁUGA ---
elif menu == "📦 Obsługa Inwentarza":
    st.title("📦 Kontrola Operacyjna")
    tab1, tab2 = st.tabs(["🔍 Lista i Zarządzanie", "📥 Nowa Dostawa"])
    
    with tab1:
        search = st.text_input("Szukaj towaru:", placeholder="Wpisz nazwę...")
        if not df_prod.empty:
            df_f = df_prod[df_prod['nazwa'].str.contains(search, case=False)]
            st.dataframe(df_f[['nazwa', 'kat_nazwa', 'liczba', 'ocena']], use_container_width=True, hide_index=True)
            
            with st.expander("🗑️ Usuwanie produktu"):
                target = st.selectbox("Wybierz do usunięcia:", df_prod['nazwa'].tolist())
                if st.button("USUŃ TRWALE", type="primary"):
                    id_d = df_prod[df_prod['nazwa'] == target]['id'].values[0]
                    supabase.table("produkty").delete().eq("id", id_d).execute()
                    st.cache_data.clear()
                    st.rerun()

    with tab2:
        if not df_kat.empty:
            k_map = {row['nazwa']: row['id'] for _, row in df_kat.iterrows()}
            with st.form("add_form", clear_on_submit=True):
                ca, cb = st.columns(2)
                p_n = ca.text_input("Nazwa produktu")
                p_k = cb.selectbox("Kategoria", options=list(k_map.keys()))
                cc, cd = st.columns(2)
                p_q = cc.number_input("Ilość", min_value=1, value=10)
                p_o = cd.slider("Ocena jakości", 0.0, 5.0, 4.0)
                if st.form_submit_button("✅ DODAJ PRODUKT", use_container_width=True):
                    if p_n:
                        supabase.table("produkty").insert({
                            "nazwa": p_n, "liczba": p_q, 
                            "ocena": p_o, "kategoria_id": k_map[p_k]
                        }).execute()
                        st.cache_data.clear()
                        st.rerun()
        else:
            st.error("Zdefiniuj kategorie w zakładce 'Konfiguracja Systemu'!")

# --- 8. MODUŁ 3: KONFIGURACJA ---
elif menu == "⚙️ Konfiguracja Systemu":
    st.title("⚙️ Struktura Bazy Danych")
    col1, col2 = st.columns([1, 2])
    with col1:
        with st.form("kat_form"):
            nk = st.text_input("Nowa Kategoria")
            ok = st.text_area("Opis")
            if st.form_submit_button("DODAJ GRUPĘ"):
                if nk:
                    supabase.table("kategorie").insert({"nazwa": nk, "opis": ok}).execute()
                    st.cache_data.clear()
                    st.rerun()
    with col2:
        if not df_kat.empty:
            st.table(df_kat[['nazwa', 'opis']])
