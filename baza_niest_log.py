import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="LOG-PRO 16", layout="wide")

# STYLE - Bardzo krótkie linie
st.markdown("""<style>
.stApp {background: #000; color: #0f0;}
h1,h2,label,p,.stMetric {color: #0f0 !important; font-weight: 900;}
button {
 background: #ff0 !important; color: #000 !important;
 font-size: 25px !important; font-weight: 900 !important;
 height: 80px !important; width: 100% !important;
 border: 4px solid #0f0 !important; border-radius: 15px !important;
}
</style>""", unsafe_allow_html=True)

# BAZA
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

# NAWIGACJA
m = st.sidebar.radio("MENU", ["📊 KPI", "📦 ZAPASY", "📈 ANALIZA", "⚙️ OPCJE"])

if m == "📊 KPI":
 st.title("STATUS OPERACYJNY")
 if not df_p.empty:
  c = st.columns(3)
  c[0].metric("TYPY (SKU)", len(df_p))
  c[1].metric("SZTUKI", int(df_p['liczba'].sum()))
  c[2].metric("JAKOŚĆ", round(df_p['ocena'].mean(), 1))
  f1 = px.pie(df_p, names='kn', values='liczba', hole=0.4, template="plotly_dark")
  st.plotly_chart(f1, use_container_width=True)
 else: st.info("Brak danych")

elif m == "📦 ZAPASY":
 st.title("ZARZĄDZANIE SKU")
 t = st.tabs(["LISTA", "DOSTAWA"])
 with t[0]:
  if not df_p.empty:
   st.dataframe(df_p[['nazwa','kn','liczba','ocena']], use_container_width=True)
   if st.button("❌ USUŃ OSTATNI"):
    db.table("produkty").delete().eq("id", df_p.iloc[-1]['id']).execute()
    st.rerun()
 with t[1]:
  with st.form("f1"):
   n = st.text_input
