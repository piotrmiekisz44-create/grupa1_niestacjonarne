import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="LOG-PRO 12.0", layout="wide")

# 1. DESIGN: Gigantyczne żółte przyciski i neonowe napisy
st.markdown("""<style>
.stApp {background: linear-gradient(rgba(0,0,0,0.8),rgba(0,0,0,0.8)), url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=1000"); background-size: cover;}
h1, h2, label, p, .stMetric {color: #00FF00 !important; font-weight: 900 !important; text-shadow: 2px 2px #000;}
div.stButton > button {
    background: #FFFF00 !important; color: #000 !important; font-size: 25px !important;
    font-weight: 900 !important; border: 5px solid #00FF00 !important;
    height: 80px !important; width: 100% !important; border-radius: 20px !important;
}
div.stButton > button:hover {background: #00FF00 !important; border-color: #FFFF00 !important;}
</style>""", unsafe_allow_html=True)

# 2. POŁĄCZENIE Z BAZĄ
@st.cache_resource
def init():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

db = init()

def load():
    try:
        p = db.table("produkty").select("*, kategorie(nazwa)").execute()
        k = db.table("kategorie").select("*").execute()
        df = pd.DataFrame(p.data)
        if not df.empty:
            df['kat_n'] = df['kategorie'].apply(lambda x: x['nazwa'] if isinstance(x, dict) else "Inne")
        return df, pd.DataFrame(k.data)
    except: return pd.DataFrame(), pd.DataFrame()

df_p, df_k = load()

# 3. INTERFEJS GŁÓWNY
st.title("🚢 LOG-PRO 12.0: COMMAND CENTER")
m = st.sidebar.radio("MENU", ["KPI", "MAGAZYN", "SYSTEM"])

if m == "KPI":
    if not df_p.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("SKU", len(df_p))
        c2.metric("SZTUKI", int(df_p['liczba'].sum()))
        c3.metric("JAKOŚĆ", f"{df_p['ocena'].mean():.1f}")
        
        st.subheader("STRUKTURA")
        f1 = px.pie(df_p, names='kat_n', values='liczba', hole=0.4, template="plotly_dark")
        st.plotly_chart(f1, use_container_width=True)
        
        st.subheader("STAN")
        f2 = px.bar(df_p, x='nazwa', y='liczba', color='ocena', template="plotly_dark")
        st.plotly_chart(f2, use_container_width=True)
    else: st.warning("Brak danych - dodaj coś w zakładce MAGAZYN")

elif m == "MAGAZYN":
    t1, t2 = st.tabs(["LISTA", "DODAJ"])
    with t1:
        if not df_p.empty:
            st.dataframe(df_p[['nazwa', 'kat_n', 'liczba', 'ocena']], use_container_width=True)
            if st.button("❌ USUŃ OSTATNI"):
                db.table("produkty").delete().eq("id", df_p.iloc[-1]['id']).execute()
                st.rerun()
    with t2:
        with st.form("f_add"):
            n = st.text_input("NAZWA")
            kn = st.selectbox("GRUPA", df_k['nazwa'].tolist() if not df_k.empty else ["?"])
            l = st.number_input("ILOŚĆ", 1)
            o = st.slider("JAKOŚĆ", 1, 5, 4)
            if st.form_submit_button("🚀 ZAPISZ DOSTAWĘ"):
                ki = df_k[df_k['nazwa'] == kn]['id'].values[0]
                db.table("produkty").insert({"nazwa":n, "kategoria_id":ki, "liczba":l, "ocena":o}).execute()
                st.rerun()

elif m == "SYSTEM":
    with st.form("f_sys"):
        nk = st.text_input("NOWA GRUPA")
        if st.form_submit_button("✅ DODAJ KATEGORIĘ"):
            db.table("kategorie").insert({"nazwa": nk}).execute()
            st.rerun()
