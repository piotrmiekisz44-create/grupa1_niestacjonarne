import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

# --- KONFIGURACJA WIZUALNA ---
st.set_page_config(
    page_title="LOG-PRO: Logistics Intelligence", 
    page_icon="🚢", 
    layout="wide"
)

# --- STYLIZACJA CSS (CIEMNY SIDEBAR I WYSOKI KONTRAST) ---
st.markdown("""
    <style>
    /* Tło branżowe: Port kontenerowy */
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.75)), 
        url("https://images.unsplash.com/photo-1494412519320-aa613dfb7738?q=80&w=2070");
        background-attachment: fixed;
        background-size: cover;
    }

    /* LEWE MENU - Głęboka czerń */
    [data-testid="stSidebar"] {
        background-color: #050505 !important;
        border-right: 2px solid #00ff88;
    }
    
    /* GŁÓWNY PANEL - Maksymalna czytelność */
    .main .block-container {
        background-color: rgba(0, 0, 0, 0.9);
        padding: 50px;
        border-radius: 20px;
        border: 1px solid rgba(0, 212, 255, 0.2);
        margin-top: 20px;
    }

    /* CZCIONKI I PRZEJRZYSTOŚĆ */
    html, body, [class*="st-"] {
        font-family: 'Segoe UI', Helvetica, sans-serif;
        color: #FFFFFF !important;
        line-height: 1.7;
    }

    h1, h2, h3 { 
        color: #00ff88 !important; 
        font-weight: 800 !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }

    /* Etykiety pól - wysoki kontrast */
    .stTextInput label, .stSelectbox label, .stNumberInput label, .stSlider label {
        color: #00d4ff !important;
        font-weight: 700 !important;
        background: rgba(0,0,0,0.4);
        padding: 4px 12px;
        border-radius: 4px;
    }

    /* Metryki KPI */
    [data-testid="stMetric"] {
        background: #111111;
        border: 2px solid #00ff88;
        border-radius: 12px;
        padding: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICJALIZACJA BAZY ---
@st.cache_resource
def init_db():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Problem z połączeniem: {e}")
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

# --- SIDEBAR NAWIGACJA ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #00ff88;'>🚢 LOG-PRO OS</h1>", unsafe_allow_html=True)
    st.divider()
    menu = st.radio(
        "WYBIERZ PANEL STEROWANIA:", 
        ["📊 Raporty Magazynowe", "📦 Obsługa Towarów", "⚙️ Struktura Bazy"],
        help="Nawiguj między analityką a zarządzaniem produktami."
    )
    st.divider()
    st.success("POŁĄCZONO Z CHMURĄ SUPABASE")

# --- MODUŁ 1: DASHBOARD ---
if menu == "📊 Raporty Magazynowe":
    st.title("📊 Analityka Terminalowa")
    st.markdown("Poniżej znajdziesz kluczowe wskaźniki stanu magazynowego (KPI) w czasie rzeczywistym.")
    
    if not df_prod.empty:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Łącznie Pozycji", len(df_prod), help="Liczba wszystkich zarejestrowanych produktów.")
        c2.metric("Suma Zapasu", int(df_prod['liczba'].sum()), help="Całkowita liczba sztuk na stanie.")
        c3.metric("Średnia Jakość", f"{df_prod['ocena'].mean():.2f} ⭐")
        
        low = len(df_prod[df_prod['liczba'] < 5])
        c4.metric("Krytyczne Braki", low, delta=f"-{low}", delta_color="inverse")

        st.divider()
        col_l, col_r = st.columns(2)
        
        with col_l:
            fig1 = px.bar(
                df_prod.groupby('kat_nazwa')['liczba'].sum().reset_index(), 
                x='kat_nazwa', y='liczba', color='liczba',
                title="Stan towarowy wg kategorii", template="plotly_dark",
                color_continuous_scale='Turbo'
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col_r:
            fig2 = px.pie(
                df_prod, names='kat_nazwa', values='liczba', hole=0.6,
                title="Procentowy udział kategorii", template="plotly_dark"
            )
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Baza danych jest pusta. Użyj panelu 'Obsługa Towarów' aby dodać asortyment.")

# --- MODUŁ 2: OBSŁUGA TOWARÓW ---
elif menu == "📦 Obsługa Towarów":
    st.title("📦 Panel Operacyjny")
    t1, t2 = st.tabs(["🔍 Przeglądaj Stany", "📥 Przyjmij Nowy Towar"])
    
    with t1:
        st.subheader("Aktualna Lista Ewidencyjna")
        st.write("Skorzystaj z pola poniżej, aby szybko odfiltrować towar po nazwie.")
        search = st.text_input("Szukaj produktu:", placeholder="Np. Kontener...")
        
        if not df_prod.empty:
            df_filtered = df_prod[df_prod['nazwa'].str.contains(search, case=False)]
            df_show = df_filtered[['nazwa', 'kat_nazwa', 'liczba', 'ocena']].copy()
            df_show.columns = ['Produkt', 'Kategoria', 'Ilość [szt]', 'Jakość']
            st.dataframe(df_show, use_container_width=True, hide_index=True)

            with st.expander("🗑️ Procedura Wycofania (Usuwanie)"):
                st.write("Wybierz produkt z listy, aby trwale usunąć go z ewidencji.")
                target = st.selectbox("Produkt do usunięcia:", df_prod['nazwa'].tolist())
                if st.button("🔴 POTWIERDŹ USUNIĘCIE", type="primary"):
                    id_to_del = df_prod[df_prod['nazwa'] == target]['id'].values[0]
                    supabase.table("produkty").delete().eq("id", id_to_del).execute()
                    st.cache_data.clear()
                    st.rerun()

    with t2:
        st.subheader("Formularz Rejestracji Dostawy")
        st.write("Wypełnij poniższe dane, aby dodać partię towaru do bazy danych.")
        if not df_kat.empty:
            k_map = {row['nazwa']: row['id'] for _, row in df_kat.iterrows()}
            with st.form("dostawa_form", clear_on_submit=True):
                ca, cb = st.columns(2)
                p_name = ca.text_input("Pełna nazwa towaru", placeholder="Np. Stal konstrukcyjna B500")
                p_kat = cb.selectbox("Przypisana Kategoria", options=list(k_map.keys()))
                
                cc, cd = st.columns(2)
                p_qty = cc.number_input("Ilość przyjęta (szt.)", min_value=1, value=10)
                p_rate = cd.slider("Weryfikacja jakości (0-5)", 0.0, 5.0, 4.0)
                
                if st.form_submit_button("✅ ZATWIERDŹ DOSTAWĘ", use_container_width=True):
                    if p_name:
                        supabase.table("produkty").insert({
                            "nazwa": p_name, "liczba": p_qty, 
                            "ocena": p_rate, "kategoria_id": k_map[p_kat]
                        }).execute()
                        st.cache_data.clear()
                        st.success(f"Towar '{p_name}' został dodany do magazynu!")
                        st.rerun()
        else:
            st.error("Wymagane: Brak kategorii w bazie. Najpierw dodaj kategorię w 'Struktura Bazy'.")

# --- MODUŁ 3: KONFIGURACJA ---
elif menu == "⚙️ Struktura Bazy":
    st.title("⚙️ Zarządzanie Architekturą")
    st.write("Tutaj możesz definiować kategorie produktów, co ułatwi późniejsze raportowanie.")
    
    cl1, cl2 = st.columns([1, 2])
    with cl1:
        st.subheader("Nowa Grupa Towarowa")
        with st.form("kat_form"):
            n_k = st.text_input("Nazwa Kategorii", placeholder="Np. Palety")
            o_k = st.text_area("Opis operacyjny")
            if st.form_submit_button("DODAJ KATEGORIĘ"):
                if n_k:
                    supabase.table("kategorie").insert({"nazwa": n_k, "opis": o_k}).execute()
                    st.cache_data.clear()
                    st.rerun
