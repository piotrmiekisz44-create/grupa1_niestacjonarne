import streamlit as st
from supabase import create_client, Client
import pandas as pd

# 1. Konfiguracja strony i połączenia
st.set_page_config(page_title="Magazyn Pro", page_icon="📦", layout="wide")

# Inicjalizacja klienta Supabase z Twoich Secrets
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# 2. Funkcja pobierania danych (z cache, aby aplikacja działała szybciej)
def get_data():
    try:
        # Pobieramy produkty wraz z danymi o kategoriach (join)
        prod_resp = supabase.table("produkty").select("*, kategorie(nazwa)").execute()
        kat_resp = supabase.table("kategorie").select("*").execute()
        
        df_p = pd.DataFrame(prod_resp.data)
        df_k = pd.DataFrame(kat_resp.data)
        
        # Przetwarzanie nazw kategorii dla wykresów
        if not df_p.empty and 'kategorie' in df_p.columns:
            df_p['kat_nazwa'] = df_p['kategorie'].apply(lambda x: x['nazwa'] if isinstance(x, dict) else "Brak")
            
        return df_p, df_k
    except Exception as e:
        st.error(f"Błąd połączenia z bazą: {e}")
        return pd.DataFrame(), pd.DataFrame()

df_prod, df_kat = get_data()

st.title("📦 System Zarządzania Magazynem")

# 3. Sekcja Analityczna (Dashboard)
st.subheader("📊 Podsumowanie Magazynu")
if not df_prod.empty:
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Liczba Produktów", len(df_prod))
    col_m2.metric("Suma Sztuk", int(df_prod['liczba'].sum()))
    col_m3.metric("Średnia Ocena", f"{df_prod['ocena'].mean():.2f} ⭐")

    # Wykres ilości produktów w podziale na kategorie
    st.write("**Ilość towaru według kategorii:**")
    chart_data = df_prod.groupby('kat_nazwa')['liczba'].sum()
    st.bar_chart(chart_data)
else:
    st.info("Baza danych jest pusta. Dodaj kategorie i produkty, aby zobaczyć statystyki.")

# Linia oddzielająca sekcje
st.divider()

# 4. Zakładki Funkcjonalne
tab1, tab2, tab3 = st.tabs(["📋 Lista Produktów", "➕ Dodaj Produkt", "📁 Zarządzaj Kategoriami"])

with tab1:
    st.subheader("Aktualny Stan")
    if not df_prod.empty:
        # Wyświetlamy sformatowaną tabelę
        df_view = df_prod[['nazwa', 'liczba', 'ocena', 'kat_nazwa']].copy()
        df_view.columns = ['Produkt', 'Ilość', 'Ocena', 'Kategoria']
        st.dataframe(df_view, use_container_width=True)
        
        # Opcja usuwania wewnątrz expandera
        with st.expander("🗑️ Usuń produkt z bazy"):
            prod_to_del = st.selectbox("Wybierz produkt", df_prod['nazwa'].tolist(), key="del_prod_select")
            if st.button("Usuń trwale", type="primary"):
                id_to_del = df_prod[df_prod['nazwa'] == prod_to_del]['id'].values[0]
                supabase.table("produkty").delete().eq("id", id_to_del).execute()
                st.success(f"Produkt {prod_to_del} został usunięty.")
                st.rerun()
    else:
        st.write("Brak produktów.")

with tab2:
    st.subheader("Formularz Nowego Produktu")
    if not df_kat.empty:
        kat_options = {row['nazwa']: row['id'] for _, row in df_kat.iterrows()}
        
        with st.form("new_product_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            n_prod = c1.text_input("Nazwa produktu")
            k_prod = c2.selectbox("Wybierz kategorię", options=list(kat_options.keys()))
            
            c3, c4 = st.columns(2)
            l_prod = c3.number_input("Ilość (sztuki)", min_value=0, step=1)
            o_prod = c4.slider("Ocena jakości", 0.0, 5.0, 4.0, 0.1)
            
            if st.form_submit_button("Zapisz w bazie"):
                if n_prod:
                    new_data = {
                        "nazwa": n_prod,
                        "liczba": l_prod,
                        "ocena": o_prod,
                        "kategoria_id": kat_options[k_prod]
                    }
                    supabase.table("produkty").insert(new_data).execute()
                    st.success("Dodano pomyślnie!")
                    st.rerun()
                else:
                    st.warning("Podaj nazwę produktu!")
    else:
        st.error("Nie możesz dodać produktu bez kategorii. Przejdź do zakładki 'Kategorie'.")

with tab3:
    st.subheader("Kategorie")
    col_k1, col_k2 = st.columns([1, 2])
    
    with col_k1:
        st.write("**Dodaj nową:**")
        with st.form("new_kat_form", clear_on_submit=True):
            n_kat = st.text_input("Nazwa kategorii")
            o_kat = st.text_area("Opis")
            if st.form_submit_button("Stwórz kategorię"):
                if n_kat:
                    supabase.table("kategorie").insert({"nazwa": n_kat, "opis": o_kat}).execute()
                    st.success("Kategoria dodana!")
                    st.rerun()

    with col_k2:
        st.write("**Istniejące kategorie:**")
        if not df_kat.empty:
            st.table(df_kat[['nazwa', 'opis']])
            # Możliwość usuwania kategorii
            kat_to_del = st.selectbox("Usuń kategorię", df_kat['nazwa'].tolist(), key="del_kat_select")
            if st.button("Usuń kategorię"):
                # Uwaga: Jeśli masz produkty w tej kategorii, baza może zablokować usunięcie (FK constraint)
                id_k_del = df_kat[df_kat['nazwa'] == kat_to_del]['id'].values[0]
                supabase.table("kategorie").delete().eq("id", id_k_del).execute()
                st.rerun()
