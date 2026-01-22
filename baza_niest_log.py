import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="LOG-PRO 18", layout="wide")

# --- 1. STYLIZACJA (CZARNE POLA I NEONY) ---
st.markdown("""<style>
.stApp {background:#000; color:#0f8;}
[data-testid="stSidebar"] {background:#050505 !important; border-right:2px solid #0f8;}
h1,h2,label,p,.stMetric {color:#0f8 !important; font-weight:900;}
/* CZARNE POLA TEKSTOWE */
input, textarea, div[data-baseweb="select"] > div {
 background:#000 !important; color:#fff !important;
 border:2px solid #0f8 !important; border-radius:8px !important;
 font-weight:bold !important;
}
/* GIGANTYCZNE ŻÓŁTE PRZYCISKI */
button {
 background:#ff0 !important; color:#000 !important;
 font-size:22px !important; font-weight:900 !important;
 height:75px !important; border-radius:15px !important;
 border:3px solid #0f8 !important; width:100% !important;
}
</style>""", unsafe_allow_html=True)

# --- 2. POŁĄCZENIE ---
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

# --- 3. MENU ---
m = st.sidebar.radio("NAWIGACJA", ["📊 ANALIZA", "📦 ZAPASY", "⚙️ SYSTEM"])

if m == "📊 ANALIZA":
 st.title("RAPORTY OPERACYJNE")
 if not df_p.empty:
  c = st.columns(3)
  c[0].metric("SKU", len(df_p))
  c[1].metric("SZTUKI", int(df_p['liczba'].sum()))
  c[2].metric("JAKOŚĆ", round(df_p['ocena'].mean(), 1))
  f1 = px.pie(df_p, names='kn', values='liczba', hole=0.4, template="plotly_dark")
  st.plotly_chart(f1, use_container_width=True)
 else: st.warning("Baza pusta. Dodaj towar w module ZAPASY.")

elif m == "📦 ZAPASY":
 st.title("KONTROLA TOWARU")
 t = st.tabs(["LISTA", "NOWA DOSTAWA"])
 with t[0]:
  if not df_p.empty:
   st.dataframe(df_p[['nazwa','kn','liczba','ocena']], use_container_width=True)
   if st.button("USUŃ OSTATNI"):
    db.table("produkty").delete().eq("id", df_p.iloc[-1]['id']).execute()
    st.rerun()
 with t[1]:
  with st.form("f1"):
   n = st.text_input("NAZWA PRODUKTU")
   g = st.selectbox("GRUPA", df_k['nazwa'].tolist() if not df_k.empty else ["?"])
   l = st.number_input("ILOŚĆ", 1)
   o = st.slider("JAKOŚĆ", 1, 5, 4)
   if st.form_submit_button("ZATWIERDŹ DOSTAWĘ"):
    ki = df_k[df_k['nazwa'] == g]['id'].values
