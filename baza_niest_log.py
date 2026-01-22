import streamlit as st
from supabase import create_client, Client
import pandas as pd

# Konfiguracja połączenia
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Magazyn Pro", page_icon="📦", layout="wide")

st.title("📦 System Zarządzania Magazynem")

# --- POBIERANIE DANYCH ---
def get_data():
    prod_resp = supabase.table("produkty").select("*, kategorie(nazwa)").execute()
    kat_resp = supabase.table("kategorie").select("*").execute()
    return pd.DataFrame(prod_resp.data), pd.DataFrame(kat_resp.data)

df_prod, df_kat = get_data()

# --- DASHBOARD (METRYKI I WYKRESY) ---
st.subheader("📊 Analityka Magazynu")
if not df_prod.empty:
    m1, m2, m3 = st.columns(3)
    m1.metric("Wszystkie Produkty", len(df_prod))
    m2.metric("Suma Stanów", int(df_prod['liczba'].sum()))
    m3.metric("Średnia Ocena", f"{df_prod['ocena'].mean():.2f} ⭐")

    # Wykres: Liczba produktów na kategorię
    # Mapujemy nazwy kategorii dla czytelności wykresu
    if 'kategorie' in df_prod.columns:
        df_prod['kat_nazwa'] = df_prod['kategorie'].apply(lambda x: x['nazwa'] if isinstance(x, dict) else "Brak")
        chart_data = df_prod.groupby('kat_nazwa')['liczba'].sum()
        st.bar_chart(chart_data)
else:
    st.info("Brak danych do wyświetlenia wykresów.")

---

# --- ZAKŁADKI ---
tab1, tab2, tab3 = st.tabs(["📋 Lista Produktów", "➕ Dodaj Nowy", "📁 Kategorie"])

with tab1:
    st.subheader("Aktualny Stan Magazynowy")
    if not df_prod.empty:
        # Wyświetlamy ładną tabelę zamiast listy
        display_df = df_prod[['nazwa', 'liczba', 'ocena', 'kat_nazwa']].copy()
        display_df.columns = ['Produkt', 'Ilość', 'Ocena', 'Kategoria']
        st.dataframe(display_df, use_container_width=True)
        
        # Sekcja usuwania (expander, aby nie zajmował miejsca)
        with st.expander("Usuń produkt"):
            prod_to_del = st.selectbox("Wybierz produkt do usunięcia", df_prod['nazwa'].tolist())
            if st.button("Potwierdź usunięcie"):
                id_to_del = df_prod[df_prod['nazwa'] == prod_to_del]['id'].values[0]
                supabase.table("produkty").delete().eq("id", id_to_del).execute()
                st.success(f"Usunięto {prod_to_del}")
                st.rerun()
    else:
        st.write("Magazyn jest pusty.")

with tab2:
    st.subheader("Nowy Produkt")
    if not df_kat.empty:
        kat_options = {row['nazwa']: row['id'] for _, row in df_kat.iterrows()}
        with st.form("add_product_form", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            nazwa = col_a.text_input("Nazwa produktu")
            kat = col_b.selectbox("Kategoria", options=list(kat_options.keys()))
            
            col_c, col_d = st.columns(2)
            liczba = col_c.number_input("Ilość", min_value=0)
            ocena = col_d.slider("Ocena", 0.0, 5.0, 2.5, 0.1)
            
            if st.form_submit_button("Dodaj do bazy"):
                if nazwa:
                    supabase.table("produkty").insert({
                        "nazwa": nazwa, "liczba": liczba, 
                        "ocena": ocena, "kategoria_id": kat_options[kat]
                    }).execute()
                    st.success("Produkt dodany!")
                    st.rerun()
    else:
        st.warning("Najpierw dodaj przynajmniej jedną kategorię!")

with tab3:
    st.subheader("Zarządzanie Kategoriami")
    c1, c2 = st.columns([1, 2])
    
    with c1:
        with st.form("add_kat"):
            n = st.text_input("Nazwa")
            o = st.text_area("Opis")
            if st.form_submit_button("Dodaj"):
                supabase.table("kategorie").insert({"nazwa": n, "opis": o}).execute()
                st.rerun()
                
    with c2:
        if not df_kat.empty:
            st.table(df_kat[['nazwa', 'opis']])
