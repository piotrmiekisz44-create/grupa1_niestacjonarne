import streamlit as st
from supabase import create_client
import pandas as pd

# 1. Połączenie z bazą
@st.cache_resource
def init_db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_db()

# 2. Pobieranie danych
def get_data():
    try:
        p = supabase.table("produkty").select("*, kategorie(nazwa)").execute()
        k = supabase.table("kategorie").select("*").execute()
        df = pd.DataFrame(p.data)
        if not df.empty:
            df['kat_nazwa'] = df['kategorie'].apply(lambda x: x['nazwa'] if isinstance(x, dict) else "Inne")
        return df, pd.DataFrame(k.data)
    except:
        return pd.DataFrame(), pd.DataFrame()

df_p, df_k = get_data()

# 3. Prosty Interfejs
st.title("📦 LOG-PRO Terminal")

menu = st.sidebar.selectbox("Menu", ["Podsumowanie", "Dodaj towar"])

if menu == "Podsumowanie":
    if not df_p.empty:
        st.metric("Liczba SKU", len(df_p))
        st.dataframe(df_p[['nazwa', 'kat_nazwa', 'liczba', 'ocena']], use_container_width=True)
    else:
        st.info("Baza jest pusta.")

elif menu == "Dodaj towar":
    with st.form("add_form"):
        n = st.text_input("Nazwa produktu")
        k = st.selectbox("Kategoria", df_k['nazwa'].tolist() if not df_k.empty else ["Brak"])
        l = st.number_input("Ilość", min_value=1, step=1)
        o = st.slider("Ocena (1-5)", 1, 5, 4)
        if st.form_submit_button("ZAPISZ"):
            kid = df_k[df_k['nazwa'] == k]['id'].values[0]
            supabase.table("produkty").insert({"nazwa": n, "kategoria_id": kid, "liczba": l, "ocena": o}).execute()
            st.success("Dodano!")
            st.rerun()
