import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="LOG-PRO 15", layout="wide")

# STYLE: Żółte przyciski i neonowe napisy
st.markdown("""<style>
.stApp {background: #111; color: #0f0;}
h1,h2,label,p,.stMetric {color: #0f0 !important; font-weight: 900 !important;}
button {
 background: yellow !important; color: black !important;
 font-size: 30px !important; font-weight: 900 !important;
 height: 100px !important; width: 100% !important;
 border: 5px solid #0f0 !important; border-radius: 20px !important;
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
   df['k'] = df['kategorie'].apply(lambda x: x['nazwa'] if isinstance(x, dict) else "Inne")
  return df, pd.DataFrame(k.data)
 except: return pd.DataFrame(), pd.DataFrame()

df_p, df_k = load()

# MENU
m = st.sidebar.radio("MENU", ["KPI", "MAGAZYN", "SYSTEM"])

if m == "KPI":
 st.title("📊 STATYSTYKI")
 if not df_p.empty:
  c1, c2, c3 = st.columns(3)
  c1.metric("SKU", len(df_p))
  c2.metric("SZTUKI", int(df_p['liczba'].sum()))
  c3.metric("JAKOŚĆ", round(df_p['ocena'].mean(), 1))
  # WYKRESY
  f1 = px.pie(df_p, names='k', values='liczba', hole=0.4, template="plotly_dark")
  st.plotly_chart(f1, use_container_width=True)
  f2 = px.bar(df_p, x='nazwa', y='liczba', color='ocena', template="plotly_dark")
  st.plotly_chart(f2, use_container_width=True)
 else: st.info("Brak danych")

elif m == "MAGAZYN":
 st.title("📦 ZASOBY")
 t1, t2 = st.tabs(["LISTA", "DODAJ"])
 with t1:
  if not df_p.empty:
   st.dataframe(df_p[['nazwa','k','liczba','ocena']], use_container_width=True)
   if st.button("USUŃ OSTATNI"):
    db.table("produkty").delete().eq("id", df_p.iloc[-1]['id']).execute()
    st.rerun()
 with t2:
  with st.form("f1"):
   n = st.text_input("NAZWA")
   kg = st.selectbox("GRUPA", df_k['nazwa'].tolist() if not df_k.empty else
