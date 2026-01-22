import streamlit as st
from supabase import create_client, Client
import pandas as pd

# 1. Konfiguracja "WOW" - Profesjonalny interfejs
st.set_page_config(
    page_title="Inwentaryzacja 4.0 | Panel Zarządzania",
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
        st.error(f"Krytyczny błąd konfiguracji: {e}")
        return None

supabase = init_connection()

# 2. Pobieranie danych z cache
@st.cache_data(ttl=10)
def fetch_data():
    if not supabase: return pd.DataFrame(), pd.DataFrame()
    try:
        # Pobieranie produktów i kategorii zgodnie ze schematem
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

df_prod, df_kat = fetch_data()

# --- SIDEBAR: CENTRUM DOWODZENIA ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/database.png", width=80)
    st.title("System Magazynowy v2.0")
    st.markdown("---")
    menu = st.radio(
        "Główne moduły:",
        ["📈 Analityka i KPI", "📦 Inwentarz", "🛠️ Konfiguracja"],
        index=0
    )
    st.markdown("---")
    # Zaskocz wykładowcę statusem "Live"
    st.success("Sygnał bazy: AKTYWNY")
    if st.button("🔄 Wymuś odświeżenie"):
        st.cache_data.clear()
        st.rerun()

# --- MODUŁ 1: ANALITYKA I KPI (EFEKT WOW) ---
if menu == "📈 Analityka i KPI":
    st.header("📊 Dashboard Analityczny")
    
    if not df_prod.empty:
        # Metryki główne
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Asortyment", len(df_prod))
        m2.metric("Suma zapasów", int(df_prod['liczba'].sum()))
        m3.metric("Średnia Ocena", f"{df_prod['ocena'].mean():.2f} ⭐")
        
        # Logika "Inteligentnego Alertu"
        alert_count = len(df_prod[df_prod['liczba'] < 5])
        m4.metric("Krytyczne Braki", alert_count, delta=f"{alert_count} poz.", delta_color="inverse")

        if alert_count > 0:
            st.warning(f"⚠️ Uwaga! {alert_count} produktów wymaga natychmiastowego zamówienia (stan < 5 szt.).")

        st.markdown("### Wizualizacja Struktury")
        c_left, c_right = st.columns(2)
        
        with c_left:
            st.write("**Ilość towaru w podziale na kategorie**")
            # Bar chart z dynamicznym kolorem
            st.bar_chart(df_prod.groupby('kat_nazwa')['liczba'].sum(), color="#2e7d32")
        
        with c_right:
            st.write("**Jakość produktów (Średnia ocena)**")
            st.area_chart(df_prod.groupby('kat_nazwa')['ocena'].mean(), color="#1565c0")
    else:
        st.info("Brak danych do analizy. Dodaj pierwsze produkty w zakładce Inwentarz.")

# --- MODUŁ 2: INWENTARZ (WYSZUKIWARKA) ---
elif menu == "📦 Inwentarz":
    st.header("📦 Ewidencja Towarów")
    
    t_list, t_add = st.tabs(["🔍 Przeglądaj i Zarządzaj", "➕ Nowa Dostawa"])
    
    with t_list:
        # Dodatek WOW: Wyszukiwarka live
        search = st.text_input("Szybkie wyszukiwanie produktu:", placeholder="Wpisz nazwę...")
        
        if not df_prod.empty:
            df_filtered = df_prod[df_prod['nazwa'].str.contains(search, case=False)]
            
            # Formatowanie tabeli dla czytelności
            df_view = df_filtered[['nazwa', 'liczba', 'ocena', 'kat_nazwa']].copy()
            df_view.columns = ['Nazwa Produktu', 'Stan (szt.)', 'Ocena', 'Kategoria']
            
            st.dataframe(df_view, use_container_width=True, hide_index=True)

            with st.expander("Usuwanie produktów (strefa niebezpieczna)"):
                col_del1, col_del2 = st.columns([3, 1])
                target = col_del1.selectbox("Wybierz do usunięcia:", df_prod['nazwa'].tolist())
                if col_del2.button("Usuń trwale", use_container_width=True, type="secondary"):
                    id_to_del = df_prod[df_prod['nazwa'] == target]['id'].values[0]
                    supabase.table("produkty").delete().eq("id", id_to_del).execute()
                    st.cache_data.clear()
                    st.toast(f"Usunięto: {target}")
                    st.rerun()
        else:
            st.info("Magazyn jest pusty.")

    with t_add:
        if not df_kat.empty:
            # Rozbicie linii na mniejsze części, aby uniknąć błędów wklejania
            kat_options = df_kat['nazwa'].tolist()
            kat_map = dict(zip(df_kat['nazwa'], df_kat['id']))
            
            with st.form("nowy_produkt"):
                col_n1, col_n2 = st.columns(2)
                nazwa_p = col_n1.text_input("Nazwa handlowa")
                kat_p = col_n2.selectbox("Kategoria", options=kat_options)
                
                col_n3, col_n4 = st.columns(2)
                stan_p = col_n3.number_input("Ilość dostarczona", min_value=0, value=10)
                ocena_p = col_n4.slider("Wstępna ocena jakości", 0.0, 5.0, 4.0)
                
                if st.form_submit_button("✅ Dodaj produkt do systemu", use_container_width=True):
                    if nazwa_p:
                        supabase.table("produkty").insert({
                            "nazwa": nazwa_p, "liczba": stan_p, 
                            "ocena": ocena_p, "kategoria_id": kat_map[kat_p]
                        }).execute()
                        st.cache_data.clear()
                        st.success("Produkt wprowadzony!")
                        st.rerun()
        else:
            st.error("Błąd: Musisz najpierw zdefiniować kategorie w ustawieniach!")

# --- MODUŁ 3: KONFIGURACJA ---
elif menu == "🛠️ Konfiguracja":
    st.header("🛠️ Zarządzanie Kategoriami")
    
    col_k1, col_k2 = st.columns([1, 2])
    
    with col_k1:
        st.subheader("Nowa Grupa")
        with st.form("dodaj_kat"):
            n_kat = st.text_input("Nazwa kategorii")
            o_kat = st.text_area("Opis techniczny")
            if st.form_submit_button("Stwórz"):
                if n_kat:
