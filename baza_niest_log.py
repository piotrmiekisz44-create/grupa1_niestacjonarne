import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# 1. Konfiguracja strony
st.set_page_config(page_title="LOG-PRO 5.0 | System Zarządzania", layout="wide", page_icon="🚚")

# 2. Stylizacja (Wyraźne czcionki i przyciski)
def apply_ui_design():
    st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
        url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070");
        background-attachment: fixed; background-size: cover;
    }
    /* Pogrubienie wszystkich etykiet i tekstów */
    label, p, .stMetric, .stSelectbox, .stSlider {
        color: white !important; font-weight: bold !important; font-size: 1.1rem !important;
    }
    /* Widoczne opisy przycisków */
    .stButton>button {
        border-radius: 20px; border: 2px solid #4CAF50;
        background-color: #1b5e20; color: white !important;
        font-weight: bold !important; width: 100%;
    }
    /* Stylizacja ramek formularzy */
    div[data-testid="stForm"] {
        background-color: rgba(0, 0, 0, 0.8);
        border: 2px solid #2e7d32; border-radius: 15px; padding: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

apply_ui_design()

# 3. Połączenie z bazą
@st.cache_resource
def init_db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

db = init_db()

# 4. Funkcje danych
def get_warehouse_data():
    try:
        p = db.table("
