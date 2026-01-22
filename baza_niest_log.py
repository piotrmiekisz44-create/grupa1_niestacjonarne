import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- KONFIGURACJA WIZUALNA ---
st.set_page_config(
    page_title="LOG-PRO ULTRA: Global Logistics OS", 
    page_icon="🌐", 
    layout="wide"
)

# --- ZAAWANSOWANY STYL (Neon-Industrial) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        background-image: radial-gradient(#1f2937 1px, transparent 1px);
        background-size: 40px 40px;
    }
    
    /* Panel główny - efekt szklany */
    .main .block-container {
        background: rgba(17, 25, 40, 0.85);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 40px;
    }

    /* Nagłówki z gradientem */
    h1, h2, h3 {
        background: linear-gradient(90deg, #00ff88, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Inter', sans-serif;
    }

    /* Karty metryk */
    [data-testid="stMetric"] {
        background: rgba(0, 255, 136, 0.05);
        border: 1px solid #00ff88;
        border-radius: 15px;
        transition: 0.3s;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 255, 136, 0.2);
    }

    /* Wysoki kontrast pól wejściowych */
    input, select, textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-weight: bold !important;
    }
    
    label {
        color: #00d4ff !important;
        font-size: 1.1rem !important;
        letter-spacing: 1px;
    }

    /* Customowe zakładki */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: rgba(0,0,0,0.3);
        padding: 10px;
        border-radius: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BACKEND: POŁĄCZENIE ---
@st.cache_resource
def init_db():
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except:
        st.error("🚨 Krytyczny błąd połączenia z satelitą bazy danych!")
        return None

supabase = init_db()

# --- ENGINE: POBIERANIE DANYCH ---
def get_all_data():
    if not supabase: return pd.DataFrame(), pd.DataFrame()
    p = supabase.table("produkty").select("*, kategorie(nazwa)").execute()
    k = supabase.table("kategorie").select("*").execute()
    df_p = pd.DataFrame(p.data)
    df_k = pd.DataFrame(k.data)
    if not df_p.empty:
        df_p['kat_nazwa'] = df_p['kategorie'].apply(lambda x: x['nazwa'] if isinstance(x, dict) else "Inne")
    return df_p, df_k

df_prod, df_kat = get_all_data()

# --- SIDEBAR (CENTRUM STEROWANIA) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2111/2111501.png", width=80)
    st.title("LOG-PRO v2.0")
    st.write("---")
    page = st.selectbox("DOK OPERACYJNY", [
        "🛸 Dashboard BI", 
        "📦 Zarządzanie Zapasami", 
        "📈 Analiza Trendów",
        "⚙️ Inżynieria Danych"
    ])
    st.info(f"Ostatnia aktualizacja: {datetime.now().strftime('%H:%M:%S')}")

# --- PAGE 1: DASHBOARD BI ---
if page == "🛸 Dashboard BI":
    st.title("🛸 Logistics Intelligence Dashboard")
    
    if not df_prod.empty:
        # Metryki w górnym rzędzie
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("SKU na stanie", len(df_prod), "📦")
        m2.metric("Wartość wolumenu", f"{int(df_prod['liczba'].sum())} j.", "⬆️")
        m3.metric("Kondycja Magazynu", f"{df_prod['ocena'].mean():.1f}/5", "⭐")
        
        braki = len(df_prod[df_prod['liczba'] < 10])
        m4.metric("Alerty braku", braki, delta=f"-{braki}" if braki > 0 else "0", delta_color="inverse")

        st.markdown("### 📊 Analiza Wizualna")
        c_left, c_right = st.columns([2, 1])

        with c_left:
            # Wykres bąbelkowy 3D-like
            fig_bubble = px.scatter(df_prod, x="liczba", y="ocena", size="liczba", color="kat_nazwa",
                                   hover_name="nazwa", title="Macierz towarowa: Ilość vs Jakość",
                                   template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_bubble, use_container_width=True)

        with c_right:
            # Wykres kołowy z "dziurką" (donut)
            fig_donut = px.pie(df_prod, names="kat_nazwa", values="liczba", hole=0.7,
                              title="Dystrybucja Kategorii", template="plotly_dark")
            fig_donut.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_donut, use_container_width=True)
    else:
        st.warning("Brak danych do analizy. Przejdź do zakładki Zarządzanie Zapasami.")

# --- PAGE 2: ZARZĄDZANIE ZAPASAMI ---
elif page == "📦 Zarządzanie Zapasami":
    st.title("📦 Centrum Operacyjne Magazynu")
    
    tab_list, tab_add, tab_del = st.tabs(["🔍 Inwentaryzacja", "➕ Nowa Partia", "❌ Likwidacja SKU"])
    
    with tab_list:
        # Zaawansowane filtrowanie
        col_f1, col_f2 = st.columns(2)
        search = col_f1.text_input("Szybkie szukanie (Produkt):")
        min_qty = col_f2.slider("Minimalna ilość na stanie:", 0, 1000, 0)
        
        filtered_df = df_prod[df_prod['nazwa'].str.contains(search, case=False)]
        filtered_df = filtered_df[filtered_df['liczba'] >= min_qty]
        
        # Kolorowanie tabeli
        def color_stock(val):
            color = '#ff4b4b' if val < 10 else '#00ff88'
            return f'color: {color}; font-weight: bold'

        if not filtered_df.empty:
            st.dataframe(filtered_df[['nazwa', 'kat_nazwa', 'liczba', 'ocena']].style.applymap(color_stock, subset=['liczba']),
                        use_container_width=True, height=400)
        
    with tab_add:
        with st.form("add_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Nazwa Produktu")
            cat = c2.selectbox("Kategoria", df_kat['nazwa'].tolist() if not df_kat.empty else ["Brak"])
            
            c3, c4 = st.columns(2)
            qty = c3.number_input("Ilość początkowa", min_value=1)
            quality = c4.select_slider("Ocena jakości przy dostawie", options=[1, 2, 3, 4, 5], value=4)
            
            if st.form_submit_button("🚀 WPROWADŹ DO EWIDENCJI"):
                cat_id = df_kat[df_kat['nazwa'] == cat]['id'].values[0]
                supabase.table("produkty").insert({"nazwa": name, "liczba": qty, "ocena": quality, "kategoria_id": cat_id}).execute()
                st.balloons()
                st.rerun()

    with tab_del:
        to_del = st.selectbox("Wybierz towar do usunięcia", df_prod['nazwa'].tolist())
        if st.button("🔥 POTWIERDŹ TRWAŁE USUNIĘCIE"):
            supabase.table("produkty").delete().eq("nazwa", to_del).execute()
            st.error(f"Produkt {to_del} usunięty.")
            st.rerun()

# --- PAGE 3: ANALIZA TRENDÓW ---
elif page == "📈 Analiza Trendów":
    st.title("📈 Predykcja i Analiza Porównawcza")
    st.info("Moduł AI szacujący optymalne stany magazynowe.")
    
    if not df_prod.empty:
        # Symulacja trendu - wykres radarowy
        st.subheader("Profil Wydajności Kategorii")
        avg_stats = df_prod.groupby('kat_nazwa')[['liczba', 'ocena']].mean().reset_
