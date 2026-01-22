import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- KONFIGURACJA UI ---
st.set_page_config(page_title="COMMANDER: Log-Pro OS", layout="wide")

# --- CUSTOM CSS: Cyber-Industrial Style ---
st.markdown("""
    <style>
    /* Globalny styl tła */
    .stApp {
        background: #050a14;
        color: #e0e0e0;
    }
    
    /* Panel nawigacyjny */
    [data-testid="stSidebar"] {
        background-color: #0a1120 !important;
        border-right: 1px solid #33ffcc;
    }

    /* Kontener główny - efekt metalicznego połysku */
    .main .block-container {
        background: linear-gradient(145deg, #0d1629, #080e1a);
        border-radius: 10px;
        border: 1px solid #1a2a4a;
        padding-top: 2rem;
    }

    /* Wygląd pól tekstowych i przycisków - Maksymalna czytelność */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        background-color: #ffffff !important;
        border-radius: 5px !important;
    }
    input {
        color: #000000 !important;
        font-weight: bold !important;
    }
    
    /* Nagłówki sekcji */
    .section-head {
        color: #33ffcc;
        text-transform: uppercase;
        letter-spacing: 2px;
        border-bottom: 2px solid #33ffcc;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }

    /* Karty statystyk */
    .metric-card {
        background: #111e35;
        border-left: 5px solid #33ffcc;
        padding: 15px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ENGINE: POŁĄCZENIE I DANE ---
@st.cache_resource
def init_db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_db()

def load_data():
    p = supabase.table("produkty").select("*, kategorie(nazwa)").execute()
    k = supabase.table("kategorie").select("*").execute()
    df_p = pd.DataFrame(p.data)
    df_k = pd.DataFrame(k.data)
    if not df_p.empty:
        df_p['kat_nazwa'] = df_p['kategorie'].apply(lambda x: x['nazwa'] if isinstance(x, dict) else "General")
    return df_p, df_k

df_p, df_k = load_data()

# --- SIDEBAR: SYSTEM CONTROL ---
with st.sidebar:
    st.markdown("<h2 style='color: #33ffcc;'>🛰️ COMMANDER v3</h2>", unsafe_allow_html=True)
    st.divider()
    app_mode = st.radio("MODUŁY SYSTEMU:", 
        ["📡 Telemetria Magazynu", "🛠️ Zarządzanie Zasobami", "🧮 Kalkulator Logistyczny"])
    
    st.divider()
    if st.button("🔄 Odśwież System"):
        st.cache_data.clear()
        st.rerun()

# --- MODUŁ 1: TELEMETRIA (WIZUALIZACJA) ---
if app_mode == "📡 Telemetria Magazynu":
    st.markdown("<h1 class='section-head'>📡 Telemetria i Status Globalny</h1>", unsafe_allow_html=True)
    
    if not df_p.empty:
        # Górne wskaźniki (KPI)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("TOTAL SKU", len(df_p))
            st.markdown("</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("STANY MAGAZYNOWE", int(df_p['liczba'].sum()))
            st.markdown("</div>", unsafe_allow_html=True)
        with col3:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("AVG QUALITY", f"{df_p['ocena'].mean():.2f}")
            st.markdown("</div>", unsafe_allow_html=True)
        with col4:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("KATEGORIE", len(df_k))
            st.markdown("</div>", unsafe_allow_html=True)

        st.write("###")
        
        # Wykresy Sunburst i Treemap
        c_left, c_right = st.columns(2)
        
        with c_left:
            st.write("#### 🗺️ Mapa Zagęszczenia Towarów")
            fig_tree = px.treemap(df_p, path=['kat_nazwa', 'nazwa'], values='liczba',
                                 color='ocena', color_continuous_scale='Viridis',
                                 template="plotly_dark")
            st.plotly_chart(fig_tree, use_container_width=True)

        with c_right:
            st.write("#### 📊 Balans Kategorii")
            fig_bar = px.bar(df_p.groupby('kat_nazwa')['liczba'].sum().reset_index(), 
                            x='kat_nazwa', y='liczba', color='liczba',
                            color_continuous_scale='GnBu', template="plotly_dark")
            st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Baza danych gotowa do przyjęcia pierwszego transportu.")

# --- MODUŁ 2: ZARZĄDZANIE (OPERACJE) ---
elif app_mode == "🛠️ Zarządzanie Zasobami":
    st.markdown("<h1 class='section-head'>🛠️ Operacje Bazodanowe</h1>", unsafe_allow_html=True)
    
    op_tab1, op_tab2 = st.tabs(["📝 Ewidencja i Edycja", "➕ Nowa Rejestracja"])
    
    with op_tab1:
        st.write("#### Przegląd systemowy")
        edited_df = st.data_editor(df_p[['id', 'nazwa', 'kat_nazwa', 'liczba', 'ocena']], 
                                  num_rows="dynamic", use_container_width=True)
        st.caption("Możesz edytować wartości bezpośrednio w tabeli (funkcja Data Editor).")

    with op_tab2:
        with st.container():
            st.write("#### 🛸 Formularz Przyjęcia Towaru")
            with st.form("new_product_form", clear_on_submit=True):
                col_a, col_b = st.columns(2)
                p_name = col_a.text_input("Nazwa Techniczna SKU")
                p_cat = col_b.selectbox("Grupa Logistyczna", df_k['nazwa'].tolist() if not df_k.empty else ["Brak"])
                
                col_c, col_d = st.columns(2)
                p_qty = col_c.number_input("Ilość Jednostkowa", min_value=1)
                p_rank = col_d.slider("Priorytet Jakości", 0.0, 5.0, 4.0)
                
                if st.form_submit_button("📥 ZATWIERDŹ DOSTAWĘ"):
                    # Logika zapisu do Supabase
                    c_id = df_k[df_k['nazwa'] == p_cat]['id'].values[0]
                    supabase.table("produkty").insert({"nazwa": p_name, "liczba": p_qty, "ocena": p_rank, "kategoria_id": c_id}).execute()
                    st.success(f"Protokół przyjęcia {p_name} wygenerowany pomyślnie!")
                    st.rerun()

# --- MODUŁ 3: KALKULATOR (NOWOŚĆ!) ---
elif app_mode == "🧮 Kalkulator Logistyczny":
    st.markdown("<h1 class='section-head'>🧮 Symulator Kosztów Składowania</h1>", unsafe_allow_html=True)
    
    st.write("Narzędzie do szacowania miesięcznych kosztów utrzymania zapasu.")
    
    col_k1, col_k2 = st.columns(2)
    with col_k1:
        cost_per_unit = st.number_input("Koszt za 1 sztukę (PLN/miesiąc):", value=2.5)
        total_stock = df_p['liczba'].sum() if not df_p.empty else 0
        st.write(f"Aktualny wolumen: **{total_stock} sztuk**")
        
    with col_k2:
        st.metric("SZACOWANY KOSZT TOTALNY", f"{total_stock * cost_per_unit:,.2f} PLN")
    
    st.divider()
    st.write("#### Symulacja wzrostu zapasów")
    growth = st.slider("Symulowany wzrost zapasów (%)", 0, 200, 50)
    simulated_stock = total_stock * (1 + growth/100)
    simulated_cost = simulated_stock * cost_per_unit
    
    st.write(f"Przy wzroście o {growth}%, koszt wyniesie: **{simulated_cost:,.2f} PLN**")
    
    # Wykres liniowy symulacji
    steps = [0, 25, 50, 75, 100, 125, 150, 175, 200]
    costs = [total_stock * (1 + s/100) * cost_per_unit for s in steps]
    fig_sim = px.line(x=steps, y=costs, labels={'x': 'Wzrost %', 'y': 'Koszt PLN'}, 
                     title="Krzywa Kosztów Składowania", markers=True, template="plotly_dark")
    st.plotly_chart(fig_sim, use_container_width=True)
