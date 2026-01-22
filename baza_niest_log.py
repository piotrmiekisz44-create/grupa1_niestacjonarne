import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="LOG-PRO 20", layout="wide")

# --- 1. STYLIZACJA (MAX WYRAŹNOŚĆ) ---
st.markdown("""<style>
/* Główne tło i teksty */
.stApp {background: #0E1117; color: #FFFFFF;}

/* NAPISY (LABELE) - Teraz będą czysto białe i pogrubione */
label, .stMarkdown p, .stSelectbox label, .stTextInput label {
    color: #FFFFFF !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    opacity: 1 !important;
}

/* POLA TEKSTOWE - Czarne tło, jasna ramka */
input, textarea, div[data-baseweb="select"] > div {
    background-color: #000000 !important;
    color: #FFFFFF !important;
    border: 2px solid #555555 !important;
    border-radius: 8px !important;
}

/* LISTY ROZWIJANE (Selectbox) - Naprawienie widoczności opcji */
div[data-baseweb="popover"] li {
    background-color: #1E1E1E !important;
    color: #FFFFFF !important;
}

/* TABELE I RAMKI - Większy kontrast */
.stDataFrame, div[data-testid="stExpander"] {
    border: 1px solid #444444 !important;
    background: #161B22 !important;
}

/* PRZYCISKI - Solidne i widoczne */
button {
    background-color: #238636 !important; /* Ciemnozielony korporacyjny */
    color: white !important;
    border: none !important;
    height: 45px !important;
    font-weight: bold !important;
}
</style>""", unsafe_allow_html=True)

# --- 2. LOGIKA BAZY ---
@st.cache_resource
def init():
    u, k = st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
    return create_client(u, k)

db = init()

def load():
    try:
        p = db.table("produkty").select("*, kategorie(nazwa)").execute()
        k = db.table("kategorie").select("*").execute()
        df = pd.DataFrame(p.data)
        if not df.empty:
            df['kn'] = df['kategorie'].apply(lambda x: x['nazwa'] if isinstance(x, dict) else "Inne")
        return df, pd.DataFrame(k.data)
    except: return pd.DataFrame(), pd.DataFrame()

df_p, df_k = load()

# --- 3. INTERFEJS ---
m = st.sidebar.radio("MENU", ["📊 Statystyki", "📦 Magazyn", "⚙️ Ustawienia"])

if m == "📊 Statystyki":
    st.title("📊 Analityka Zasobów")
    if not df_p.empty:
        c = st.columns(3)
        c[0].metric("Produkty", len(df_p))
        c[1].metric("Suma sztuk", int(df_p['liczba'].sum()))
        c[2].metric("Śr. Jakość", round(df_p['ocena'].mean(), 1))
        f1 = px.bar(df_p, x='kn', y='liczba', color='ocena', template="plotly_dark")
        st.plotly_chart(f1, use_container_width=True)
    else: st.info("Baza danych jest aktualnie pusta.")

elif m == "📦 Magazyn":
    st.title("📦 Ewidencja Towaru")
    t1, t2 = st.tabs(["Lista towarów", "Dodaj dostawę"])
    with t1:
        if not df_p.empty:
            st.dataframe(df_p[['nazwa','kn','liczba','ocena']], use_container_width=True, hide_index=True)
            with st.expander("Usuń produkt z systemu"):
                sel = st.selectbox("Wybierz nazwę:", df_p['nazwa'].tolist())
                if st.button("Potwierdź usunięcie"):
                    db.table("produkty").delete().eq("id", df_p[df_p['nazwa']==sel]['id'].values[0]).execute()
                    st.cache_data.clear()
                    st.rerun()
    with t2:
        with st.form("form_add"):
            n = st.text_input("Pełna nazwa produktu")
            g = st.selectbox("Wybierz kategorię", df_k['nazwa'].tolist() if not df_k.empty else ["Brak"])
            l = st.number_input("Ilość (sztuki)", min_value=0, step=1)
            o = st.slider("Ocena jakości", 1.0, 5.0, 4.0)
            if st.form_submit_button("Zapisz w bazie danych"):
                ki = df_k[df_k['nazwa']==g]['id'].values[0]
                db.table("produkty").insert({"nazwa":n, "kategoria_id":ki, "liczba":l, "ocena":o}).execute()
                st.cache_data.clear()
                st.rerun()

elif m == "⚙️ Ustawienia":
    st.title("⚙️ Zarządzanie strukturą")
    with st.form("form_kat"):
        nk = st.text_input("Nazwa nowej kategorii (np. Mrożonki)")
        if st.form_submit_button("Dodaj kategorię"):
            db.table("kategorie").insert({"nazwa": nk}).execute()
            st.cache_data.clear()
            st.rerun()
    if not df_k.empty:
        st.write("Aktualne kategorie:")
        st.table(df_k[['nazwa']])
