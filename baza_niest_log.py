import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="LOG-PRO 19", layout="wide")

# --- 1. STYLIZACJA (PROFESIONAL DARK) ---
st.markdown("""<style>
/* Tło i teksty - Stonowane kolory */
.stApp {background: #121212; color: #E0E0E0;}
[data-testid="stSidebar"] {background: #1E1E1E !important; border-right: 1px solid #333;}
h1, h2, h3, label {color: #B0BEC5 !important; font-weight: 600 !important;}

/* CZYTELNE LISTY I TABELE */
.stDataFrame, .stTable {background: #1E1E1E !important; border-radius: 10px;}
div[data-testid="stExpander"] {background: #1E1E1E !important; border: 1px solid #333;}

/* CZARNE POLA TEKSTOWE - WYRAŹNE */
input, textarea, div[data-baseweb="select"] > div {
 background: #000000 !important; color: #FFFFFF !important;
 border: 1px solid #455A64 !important; border-radius: 5px !important;
}

/* PRZYCISKI - MNIEJ RAŻĄCE, CZYTELNE */
button {
 background: #37474F !important; color: white !important;
 font-weight: 600 !important; height: 50px !important;
 border: 1px solid #546E7A !important; width: 100% !important;
 border-radius: 8px !important;
}
button:hover {background: #455A64 !important; border-color: #00BCD4 !important;}

/* Poprawa czytelności selectbox (listy rozwijanej) */
div[data-baseweb="popover"] {background: #1E1E1E !important; color: white !important;}
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
m = st.sidebar.radio("MODUŁY", ["📊 Dashboard", "📦 Magazyn", "⚙️ Ustawienia"])

if m == "📊 Dashboard":
 st.title("Analityka Zasobów")
 if not df_p.empty:
  c = st.columns(3)
  c[0].metric("Liczba SKU", len(df_p))
  c[1].metric("Suma Stanów", int(df_p['liczba'].sum()))
  c[2].metric("Śr. Jakość", round(df_p['ocena'].mean(), 1))
  f1 = px.bar(df_p, x='kn', y='liczba', color='ocena', template="plotly_dark", title="Stany w kategoriach")
  st.plotly_chart(f1, use_container_width=True)
 else: st.info("Brak danych do analizy.")

elif m == "📦 Magazyn":
 st.title("Zarządzanie Produktami")
 t1, t2 = st.tabs(["📋 Ewidencja", "➕ Nowy Artykuł"])
 with t1:
  if not df_p.empty:
   # Czytelna tabela
   st.dataframe(df_p[['nazwa','kn','liczba','ocena']], use_container_width=True, hide_index=True)
   with st.expander("Usuwanie produktu"):
    sel = st.selectbox("Wybierz do usunięcia:", df_p['nazwa'].tolist())
    if st.button("Usuń zaznaczony"):
     db.table("produkty").delete().eq("id", df_p[df_p['nazwa']==sel]['id'].values[0]).execute()
     st.rerun()
 with t2:
  with st.form("add_form"):
   n = st.text_input("Nazwa produktu")
   g = st.selectbox("Kategoria", df_k['nazwa'].tolist() if not df_k.empty else ["Brak"])
   l = st.number_input("Ilość", 1)
   o = st.slider("Ocena", 1, 5, 3)
   if st.form_submit_button("Dodaj do bazy danych"):
    ki = df_k[df_k['nazwa']==g]['id'].values[0]
    db.table("produkty").insert({"nazwa":n, "kategoria_id":ki, "liczba":l, "ocena":o}).execute()
    st.rerun()

elif m == "⚙️ Ustawienia":
 st.title("Konfiguracja Systemu")
 with st.form("kat_form"):
  nk = st.text_input("Nazwa nowej kategorii")
  if st.form_submit_button("Utwórz kategorię"):
   db.table("kategorie").insert({"nazwa": nk}).execute()
   st.rerun()
