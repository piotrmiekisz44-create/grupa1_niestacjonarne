import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="LOG-PRO 8.0", layout="wide")

# CSS - Bardzo krótkie linie
st.markdown("""<style>
.stApp {background: linear-gradient(rgba(0,0,0,0.8),rgba(0,0,0,0.8)), url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=800"); background-size: cover;}
label, p, .stMetric {color: white !important; font-weight: bold !important;}
button {background: #00FF00 !important; color: black !important; font-weight: bold !important; border: 2px solid white !important;}
</style>""", unsafe_allow_html=True)

# DB - Uproszczone nazwy
@st.cache_resource
def db_init():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

db = db_init()

def get_data():
    try:
        p = db.table("produkty").select("*, kategorie(nazwa)").execute()
        k = db.table("kategorie").select("*").execute()
        df = pd.DataFrame(p.data)
        if not df.empty:
            df['k'] = df['kategorie'].apply(lambda x: x['nazwa'] if isinstance(x, dict) else "Inne")
        return df, pd.DataFrame(k.data)
    except: return pd.DataFrame(), pd.DataFrame()

df_p, df_k = get_data()

# INTERFEJS
st.title("🚢 LOG-PRO 8.0")
pg = st.sidebar.radio("MENU", ["KPI", "SKU", "SET"])

if pg == "KPI":
    if not df_p.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("SKU", len(df_p))
        c2.metric("SZT", int(df_p['liczba'].sum()))
        c3.metric("OCENA", round(df_p['ocena'].mean(), 1))
        st.plotly_chart(px.pie(df_p, names='k', values='liczba', hole=0.4, template="dark"))
        st.plotly_chart(px.bar(df_p, x='k', y='liczba', color='ocena', template="dark"))
    else: st.warning("Brak danych")

elif pg == "SKU":
    t1, t2 = st.tabs(["LISTA", "DODAJ"])
    with t1:
        if not df_p.empty:
            st.dataframe(df_p[['nazwa', 'k', 'liczba', 'ocena']], use_container_width=True)
            if st.button("USUŃ"):
                db.table("produkty").delete().eq("id", df_p.iloc[-1]['id']).execute()
                st.rerun()
    with t2:
        with st.form("f1"):
            n = st.text_input("NAZWA")
            kg = st.selectbox("GRUPA", df_k['nazwa'].tolist() if not df_k.empty else ["?"])
            l = st.number_input("ILOŚĆ", 1)
            o = st.slider("JAKOŚĆ", 1, 5, 4)
            if st.form_submit_button("ZAPISZ"):
                ki = df_k[df_k['nazwa'] == kg]['id'].values[0]
                db.table("produkty").insert({"nazwa":n, "kategoria_id":ki, "liczba":l, "ocena":o}).execute()
                st.rerun()

elif pg == "SET":
    with st.form("f2"):
        nk = st.text_input("NOWA GRUPA")
        if st.form_submit_button("DODAJ"):
            db.table("kategorie").insert({"nazwa": nk}).execute()
            st.rerun()
