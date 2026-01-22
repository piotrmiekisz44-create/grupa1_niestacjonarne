import streamlit as st
from supabase import create_client, Client
import pandas as pd

# 1. Konfiguracja strony
st.set_page_config(
    page_title="Zarządzanie Magazynem", 
    page_icon="📝", 
    layout="wide"
)

# Inicjalizacja klienta Supabase
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# 2. Funkcja pobierania danych
def get_data():
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
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame()

df_prod, df_kat = get_data()

# --- PANEL GŁÓWNY ---
st.title("➕ Dodaj nowy produkt")

if not df_kat.empty:
    kat_map = {row['nazwa']: row['id'] for _, row in df_kat.iterrows()}
    
    with st.container(border=True):
        with st.form("main_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                n_prod = st.text_input("Nazwa produktu")
                k_prod = st.selectbox("Kategoria", options=list(kat_map.keys()))
            with col2:
                l_prod = st.number_input("Ilość", min_value=0, step=1)
                o_prod = st.slider("Ocena", 0.0, 5.0, 4.0, 0.1)
            
            # ROZBITA LINIA (aby uniknąć błędu):
            submit = st.form_submit_button(
                label="Zapisz produkt w magazynie", 
                use_container_width=True, 
                type="primary"
            )
            
            if submit:
                if n_prod:
                    supabase.table("produkty").insert({
                        "nazwa": n_prod, 
                        "liczba": l_prod, 
                        "ocena": o_prod, 
                        "kategoria_id": kat_map[k_prod]
                    }).execute()
                    st.success(f"Dodano: {n_prod}")
                    st.rerun()
else:
    st.warning("Brak kategorii w bazie.")

st.divider()

# --- ZAKŁADKI ---
t1, t2, t3 = st.tabs(["📋 Lista", "📊 Wykresy", "⚙️ Kategorie"])

with t1:
    if not df_prod.empty:
        df_v = df_prod[['nazwa', 'liczba', 'ocena', 'kat_nazwa']].copy()
        df_v.columns = ['Produkt', 'Ilość', 'Ocena', 'Kategoria']
        st.dataframe(df_v, use_container_width=True)
        
        with st.expander("Usuń produkt"):
            del_n = st.selectbox("Wybierz do usunięcia", df_prod['nazwa'].tolist())
            if st.button("Potwierdź usunięcie"):
                id_d = df_prod[df_prod['nazwa'] == del_n]['id'].values[0]
                supabase.table("produkty").delete().eq("id", id_d).execute()
                st.rerun()

with t2:
    if not df_prod.empty:
        c_a, c_b = st.columns(2)
        with c_a:
            st.write("**Ilość w kategoriach**")
            st.bar_chart(df_prod.groupby('kat_nazwa')['liczba'].sum())
        with c_b:
            st.write("**Średnie oceny**")
            st.line_chart(df_prod.groupby('kat_nazwa')['ocena'].mean())
    else:
        st.info("Brak danych do wykresów.")

with t3:
    st.subheader("Nowa kategoria")
    with st.form("k_form"):
        nk = st.text_input("Nazwa")
        ok = st.text_area("Opis")
        if st.form_submit_button("Dodaj"):
            if nk:
                supabase.table("kategorie").insert({"nazwa": nk, "opis": ok}).execute()
                st.rerun()
