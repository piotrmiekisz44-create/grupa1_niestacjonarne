import streamlit as st
from supabase import create_client, Client

# Konfiguracja połączenia z Supabase
# Dane powinny być przechowywane w "Secrets" na Streamlit Cloud
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.title("📦 System Zarządzania Produktami")

# --- ZAKŁADKI ---
tab1, tab2 = st.tabs(["Produkty", "Kategorie"])

# --- SEKCJA: KATEGORIE ---
with tab2:
    st.header("Zarządzanie Kategoriami")
    
    # Formularz dodawania kategorii
    with st.form("add_category"):
        nazwa_kat = st.text_input("Nazwa kategorii")
        opis_kat = st.text_area("Opis")
        submit_kat = st.form_submit_button("Dodaj kategorię")
        
        if submit_kat and nazwa_kat:
            data = {"nazwa": nazwa_kat, "opis": opis_kat}
            supabase.table("kategorie").insert(data).execute()
            st.success("Dodano kategorię!")
            st.rerun()

    # Wyświetlanie i usuwanie kategorii
    st.subheader("Lista Kategorii")
    kategorie = supabase.table("kategorie").select("*").execute()
    for kat in kategorie.data:
        col1, col2 = st.columns([4, 1])
        col1.write(f"**{kat['nazwa']}** - {kat['opis']}")
        if col2.button("Usuń", key=f"del_kat_{kat['id']}"):
            supabase.table("kategorie").delete().eq("id", kat['id']).execute()
            st.rerun()

# --- SEKCJA: PRODUKTY ---
with tab1:
    st.header("Zarządzanie Produktami")
    
    # Pobranie kategorii do selectboxa
    kategorie_data = supabase.table("kategorie").select("id, nazwa").execute().data
    kat_options = {k['nazwa']: k['id'] for k in kategorie_data}

    # Formularz dodawania produktu
    with st.form("add_product"):
        nazwa_prod = st.text_input("Nazwa produktu")
        liczba = st.number_input("Liczba", min_value=0, step=1)
        ocena = st.number_input("Ocena", min_value=0.0, max_value=5.0, step=0.1)
        kat_id = st.selectbox("Kategoria", options=list(kat_options.keys()))
        submit_prod = st.form_submit_button("Dodaj produkt")
        
        if submit_prod and nazwa_prod:
            product_data = {
                "nazwa": nazwa_prod,
                "liczba": liczba,
                "ocena": ocena,
                "kategoria_id": kat_options[kat_id]
            }
            supabase.table("produkty").insert(product_data).execute()
            st.success("Dodano produkt!")
            st.rerun()

    # Wyświetlanie i usuwanie produktów
    st.subheader("Lista Produktów")
    produkty = supabase.table("produkty").select("*, kategorie(nazwa)").execute()
    
    for prod in produkty.data:
        col1, col2 = st.columns([4, 1])
        kat_name = prod.get('kategorie', {}).get('nazwa', 'Brak')
        col1.write(f"**{prod['nazwa']}** | Ilość: {prod['liczba']} | Kat: {kat_name}")
        if col2.button("Usuń", key=f"del_prod_{prod['id']}"):
            supabase.table("produkty").delete().eq("id", prod['id']).execute()
            st.rerun()
