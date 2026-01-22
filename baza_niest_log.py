import streamlit as st
from supabase import create_client, Client
import pandas as pd

# 1. Konfiguracja strony - Professional Look
st.set_page_config(
    page_title="Warehouse Intelligence Pro",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicjalizacja klienta Supabase
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# 2. Funkcja pobierania danych (optymalizacja)
@st.cache_data(ttl=60) # Odświeżanie cache co 60 sekund
def get_data():
    try:
        p_res = supabase.table("produkty").select("*, kategorie(nazwa)").execute()
        k_res = supabase.table("kategorie").select("*").execute()
        df_p = pd.DataFrame(p_res.data)
        df_k = pd.DataFrame(k_res.data)
        if not df_p.empty and 'kategorie' in df_p.columns:
            df_p['kat_nazwa'] = df_p['kategorie'].apply(
                lambda x: x['nazwa'] if isinstance(x, dict) else "Niezdefiniowana"
            )
        return df_p, df_k
    except Exception:
        return pd.DataFrame(), pd.DataFrame()

df_prod, df_kat = get_data()

# --- SIDEBAR: NAWIGACJA I FILTRY ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/warehouse.png", width=80)
    st.title("Menu Systemu")
    menu = st.radio(
        "Wybierz moduł:",
        ["🏠 Pulpit Menadżera", "📦 Zarządzanie Produktami", "📁 Kategorie i Ustawienia"]
    )
    st.divider()
    st.info("System połączony z bazą Supabase w chmurze.")

# --- MODUŁ 1: PULPIT MENADŻERA (DASHBOARD) ---
if menu == "🏠 Pulpit Menadżera":
    st.title("📊 Inteligentny Pulpit Magazynowy")
    
    if not df_prod.empty:
        # Metryki na górze
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Asortyment", len(df_prod))
        m2.metric("Suma zapasów", int(df_prod['liczba'].sum()))
        m3.metric("Średnia ocena", f"{df_prod['ocena'].mean():.2f} ⭐")
        low_stock = len(df_prod[df_prod['liczba'] < 5])
        m4.metric("Niski stan (<5)", low_stock, delta=-low_stock, delta_color="inverse")

        st.divider()
        
        # Wykresy
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📦 Struktura zapasów")
            chart_data = df_prod.groupby('kat_nazwa')['liczba'].sum()
            st.bar_chart(chart_data, color="#1f77b4")
        
        with c2:
            st.subheader("⭐ Ranking jakości")
            avg_rating = df_prod.groupby('kat_nazwa')['ocena'].mean()
            st.area_chart(avg_rating, color="#ff7f0e")
            
        
    else:
        st.warning("Baza danych jest obecnie pusta. Dodaj pierwsze produkty.")

# --- MODUŁ 2: ZARZĄDZANIE PRODUKTAMI ---
elif menu == "📦 Zarządzanie Produktami":
    st.title("📦 Kontrola Inwentarza")
    
    # Przycisk odświeżania
    if st.button("🔄 Odśwież dane"):
        st.cache_data.clear()
        st.rerun()

    tab_view, tab_add = st.tabs(["🔍 Przeglądaj i Usuń", "➕ Dodaj Nowy Produkt"])

    with tab_view:
        if not df_prod.empty:
            # Wyszukiwarka
            search = st.text_input("Szukaj produktu po nazwie...", "")
            filtered_df = df_prod[df_prod['nazwa'].str.contains(search, case=False)]
            
            # Tabela
            df_v = filtered_df[['nazwa', 'liczba', 'ocena', 'kat_nazwa']].copy()
            df_v.columns = ['Produkt', 'Ilość (szt.)', 'Ocena Jakości', 'Kategoria']
            st.dataframe(df_v, use_container_width=True, hide_index=True)

            # Akcja usuwania
            with st.expander("Panel usuwania produktów"):
                del_prod = st.selectbox("Wybierz produkt do wycofania:", df_prod['nazwa'].tolist())
                if st.button("🔴 Usuń trwale z magazynu", type="secondary"):
                    id_to_del = df_prod[df_prod['nazwa'] == del_prod]['id'].values[0]
                    supabase.table("produkty").delete().eq("id", id_to_del).execute()
                    st.cache_data.clear()
                    st.success(f"Produkt {del_prod} został pomyślnie usunięty.")
                    st.rerun()
        else:
            st.info("Brak produktów do wyświetlenia.")

    with tab_add:
        if not df_kat.empty:
            kat_map = {row['nazwa']: row['id'] for _, row in df_kat.iterrows()}
            with st.form("professional_add_form"):
                col_a, col_b = st.columns(2)
                p_name = col_a.text_input("Oficjalna nazwa produktu")
                p_kat = col_b.selectbox("Kategoria systemowa", options=list(kat_map.keys()))
                
                col_c, col_d = st.columns(2)
                p_count = col_c.number_input("Ilość dostawy", min_value=0, step=1)
                p_score = col_d.slider("Weryfikacja jakości (ocena)", 0.0, 5.0, 4.0)
                
                if st.form_submit_button("✅ Zatwierdź i wprowadź do bazy", use_container_width=True):
                    if p_name:
                        supabase.table("produkty").insert({
                            "nazwa": p_name, "liczba": p_count,
                            "ocena": p_score, "kategoria_id": kat_map[p_kat]
                        }).execute()
                        st.cache_data.clear()
                        st.toast(f"Dodano produkt: {p_name}")
                        st.rerun()
        else:
            st.error("Wymagane zdefiniowanie kategorii przed dodaniem produktów.")

# --- MODUŁ 3: KATEGORIE I USTAWIENIA ---
elif menu == "📁 Kategorie i Ustawienia":
    st.title("⚙️ Konfiguracja Systemu")
    
    col_k1, col_k2 = st.columns([1, 2])
    
    with col_k1:
        st.subheader("Nowa Grupa")
        with st.form("kat_add_pro"):
            nk = st.text_input("Nazwa kategorii")
            ok = st.text_area("Opis operacyjny")
            if st.form_submit_button("Dodaj kategorię"):
                if nk:
                    supabase.table("kategorie").insert({"nazwa": nk, "opis": ok}).execute()
                    st.cache_data.clear()
                    st.rerun()

    with col_k2:
        st.subheader("Istniejące Struktury")
        if not df_kat.empty:
            st.table(df_kat[['nazwa', 'opis']])
