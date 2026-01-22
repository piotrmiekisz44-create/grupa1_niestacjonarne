import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="LOG-PRO 17", layout="wide")

# 1. STYLE - Maksymalna widoczność
st.markdown("""<style>
.stApp {background: #000; color: #0f0;}
h1,h2,label,p,.stMetric {color: #0f0 !important; font-weight: 900;}
button {
 background: #ff0 !important; color: #000 !important;
 font-size: 24px !important; font-weight: 900 !important;
 height: 85px !important; width: 100% !important;
 border: 4px solid #0f0 !important; border-radius: 20px !important;
}
</style>""", unsafe_allow_html=True)

# 2. BAZA DANYCH
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

# 3. NAWIGACJA I MODUŁY
m = st.sidebar.radio("MODUŁ OPERACYJNY", ["📊 KPI", "📦 DOSTAWY", "📈 ANALIZA", "⚙️ SYSTEM"])

if m == "📊 KPI":
 st.title("GŁÓWNY PANEL KPI")
 if not df_p.empty:
  c = st.columns(3)
  c[0].metric("SKU (TYPY)", len(df_p))
  c[1].metric("SZTUKI", int(df_p['liczba'].sum()))
  c[2].metric("JAKOŚĆ", round(df_p['ocena'].mean(), 1))
  # WYKRES STRUKTURY
  f1 = px.pie(df_p, names='kn', values='liczba', hole=0.4)
  f1.update_layout(template="plotly_dark", margin=dict(t=0,b=0,l=0,r=0))
  st.plotly_chart(f1, use_container_width=True)
 else: st.info("Brak danych - dodaj pierwszy produkt w sekcji DOSTAWY.")

elif m == "📦 DOSTAWY":
 t = st.tabs(["🔍 EWIDENCJA", "➕ PRZYJĘCIE"])
 with t[0]:
  if not df_p.empty:
   st.dataframe(df_p[['nazwa','kn','liczba','ocena']], use_container_width=True)
   if st.button("❌ USUŃ OSTATNI"):
    db.table("produkty").delete().eq("id", df_p.iloc[-1]['id']).execute()
    st.rerun()
 with t[1]:
  with st.form("f1"):
   n = st.text_input("NAZWA TOWARU")
   g = st.selectbox("GRUPA", df_k['nazwa'].tolist() if not df_k.empty else ["?"])
   l = st.number_input("ILOŚĆ (SZT)", 1)
   o = st.slider("KLASA JAKOŚCI", 1, 5, 4)
   if st.form_submit_button("🚀 ZAREJESTRUJ DOSTAWĘ"):
    ki = df_k[df_k['nazwa'] == g]['id'].values[0]
    db.table("produkty").insert({"nazwa":n,"kategoria_id":ki,"liczba":l,"ocena":o}).execute()
    st.rerun()

elif m == "📈 ANALIZA":
 st.title("ANALITYKA TOWAROWA")
 if not df_p.empty:
  st.subheader("ROZKŁAD ILOŚCI DO JAKOŚCI")
  f2 = px.scatter(df_p, x='liczba', y='ocena', size='liczba', color='kn', hover_name='nazwa')
  f2.update_layout(template="plotly_dark")
  st.plotly_chart(f2, use_container_width=True)
  st.download_button("Pobierz Raport CSV", df_p.to_csv(index=False), "magazyn.csv")
 else: st.warning("Zbyt mało danych do generowania analizy.")

elif m == "⚙️ SYSTEM":
 st.title("USTAWIENIA BAZY")
 with st.form("f2"):
  nk = st.text_input("NAZWA NOWEJ GRUPY")
  if st.form_submit_button("✅ DODAJ KATEGORIĘ"):
   db.table("kategorie").insert({"nazwa": nk}).execute()
   st.rerun()
