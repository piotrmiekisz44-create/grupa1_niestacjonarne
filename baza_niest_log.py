import streamlit as st
from supabase import create_client, Client
import pandas as pd

# 1. Konfiguracja strony - Profesjonalny Layout
st.set_page_config(
    page_title="Inwentaryzacja 4.0 Pro",
    page_icon="🚀",
    layout="wide"
)

# Inicjalizacja połączenia
@st.cache_resource
def init_connection():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Błąd konfiguracji: {e}")
        return None

supabase = init_connection()

# 2. Pobieranie danych (z cache dla szybkości)
@st.cache_data(ttl=10)
def fetch_data():
    if not supabase: return pd.DataFrame(), pd.DataFrame()
    try:
        p_res = supabase.table("produkty").select("*, kategorie(nazwa)").execute()
        k_res = supabase.table("kategorie").select("*").execute()
        
        df_p = pd.DataFrame(p_res.data)
        df_k = pd.DataFrame(k_res.data)
        
        if not df_p.empty and 'kategorie' in df_p.columns:
            # Mapowanie nazwy kategorii zgodnie ze schematem
            df_p['kat_nazwa'] = df_p['kategorie'].apply(
                lambda x: x['nazwa'] if isinstance(x, dict) else "Brak"
            )
        return df_p, df_k
    except Exception:
        return pd.DataFrame(), pd.DataFrame()

df_prod, df_kat = fetch_data()

# --- SIDEBAR: CENTRUM DOWODZENIA ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/database.png", width=80)
    st.title("System Magazynowy")
    st.markdown("---")
    menu = st.radio(
        "Główne moduły:",
        ["📈 Analityka", "📦 Inwentarz", "🛠️ Ustawienia"],
        index=0
    )
    st.markdown("---")
    st.success("Baza danych: POŁĄCZONO")
    if st.button("🔄 Odśwież system"):
        st.cache_data.clear()
        st.rerun()

# --- MODUŁ 1: ANALITYKA (EFEKT WOW) ---
if menu == "📈 Analityka":
    st.header("📊 Dashboard Zarządczy")
    
    if not df_prod.empty:
        # KPI - Kluczowe wskaźniki
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Unikalne Produkty", len(df_prod))
        m2.metric("Łączny Stan", int(df_prod['liczba'].sum()))
        m3.metric("Średnia Jakość", f"{df_prod['ocena'].mean():.2f} ⭐")
        
        # System alertów o niskim stanie
        alert_count = len(df_prod[df_prod['liczba'] < 5])
        m4.metric("Braki (stan < 5)", alert_count, delta_color="inverse")

        if alert_count > 0:
            st.error(f"🚨 ALERT: {alert_count} pozycji wymaga domówienia!")

        st.divider()
        c_left, c_right = st.columns(2)
        with c_left:
            st.subheader("Stany wg Kategorii")
            st.bar_chart(df_prod.groupby('kat_nazwa')['liczba'].sum())
        with c_right:
            st.subheader("Oceny Kategorii")
            st.area_chart(df_prod.groupby('kat_nazwa')['ocena'].mean())
    else:
        st.info("Baza jest pusta. Przejdź do Inwentarza, by dodać produkty.")

# --- MODUŁ 2: INWENTARZ ---
elif menu == "📦 Inwentarz":
    st.header("📦 Ewidencja Towarów")
    
    t_list, t_add = st.tabs(["🔍 Przegląd", "➕ Nowa Dostawa"])
    
    with t_list:
        search = st.text_input("Szukaj produktu...", placeholder="Wpisz nazwę...")
        if not df_prod.empty:
            df_f = df_prod[df_prod['nazwa'].str.contains(search, case=False)]
            # Zmiana nazw kolumn dla interfejsu
            df_v = df_f[['nazwa', 'liczba', 'ocena', 'kat_nazwa']].copy()
            df_v.columns = ['Produkt', 'Ilość', 'Ocena', 'Kategoria']
            st.dataframe(df_v, use_container_width=True, hide_index=True)

            with st.expander("Usuwanie produktu"):
                target = st.selectbox("Wybierz do usunięcia", df_prod['nazwa'].tolist())
                if st.button("🔴 Usuń trwale"):
                    id_to_del = df_prod[df_prod['nazwa'] == target]['id'].values[0]
                    supabase.table("produkty").delete().eq("id", id_to_del).execute()
                    st.cache_data.clear()
                    st.rerun()
        else:
            st.info("Brak produktów.")

    with t_add:
        if not df_kat.empty:
            k_map = {row['nazwa']: row['id'] for _, row in df_kat.iterrows()}
            with st.form("add_product_form", clear_on_submit=True):
                col_n1, col_n2 = st.columns(2)
                n = col_n1.text_input("Nazwa handlowa")
                k = col_n2.selectbox("Kategoria", options=list(k_map.keys()))
                
                col_n3, col_n4 = st.columns(2)
                l = col_n3.number_input("Sztuk w dostawie", min_value=0)
                o = col_n4.slider("Ocena partii", 0.0, 5.0, 4.0)
                
                if st.form_submit_button("✅ Zatwierdź dostawę", use_container_width=True):
                    if n:
                        supabase.table("produkty").insert({
                            "nazwa": n, "liczba": l, 
                            "ocena": o, "kategoria_id": k_map[k]
                        }).execute()
                        st.cache_data.clear()
                        st.success("Zapisano!")
                        st.rerun()
        else:
            st.warning("Najpierw dodaj kategorie w Ustawieniach!")

# --- MODUŁ 3: USTAWIENIA (Tu naprawiono IndentationError) ---
elif menu == "🛠️ Ustawienia":
    st.header("🛠️ Konfiguracja Systemu")
    
    c_k1, c_k2 = st.columns([1, 2])
    
    with c_k1:
        st.subheader("Nowa Grupa")
        with st.form("dodaj_kat"):
            n_kat = st.text_input("Nazwa")
            o_kat = st.text_area("Opis")
            if st.form_submit_button("Dodaj"):
                if n_kat:
                    # Tutaj naprawione wcięcie!
                    supabase.table("kategorie").insert({
                        "nazwa": n_kat, 
                        "opis": o_kat
                    }).execute()
                    st.cache_data.clear()
                    st.rerun()

    with c_k2:
        st.subheader("Aktualne Kategorie")
        if not df_kat.empty:
            st.table(df_kat[['nazwa', 'opis']])
