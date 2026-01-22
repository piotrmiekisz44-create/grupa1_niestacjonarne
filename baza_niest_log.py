import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

# --- KONFIGURACJA WIZUALNA ---
st.set_page_config(
    page_title="LOG-PRO: Logistics Intelligence", 
    page_icon="🚢", 
    layout="wide"
)

# --- STYLIZACJA CSS (CIEMNY SIDEBAR I WYSOKI KONTRAST) ---
st.markdown("""
    <style>
    /* Tło branżowe: Port kontenerowy */
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.75)), 
        url("https://images.unsplash.com/photo-1494412519320-aa613dfb7738?q=80&w=2070");
        background-attachment: fixed;
        background-size: cover;
    }

    /* LEWE MENU - Głęboka czerń */
    [data-testid="stSidebar"] {
        background-color: #050505 !important;
        border-right: 2px solid #00ff88;
    }
    
    /* GŁÓWNY PANEL - Maksymalna czytelność */
    .main .block-container {
        background-color: rgba(0, 0, 0, 0.9);
        padding: 50px;
        border-radius: 20px;
        border: 1px solid rgba(0, 212, 255, 0.2);
        margin-top: 20px;
    }

    /* CZCIONKI I PRZEJRZYSTOŚĆ */
    html, body, [class*="st-"] {
        font-family: 'Segoe UI', Helvetica, sans-serif;
        color: #FFFFFF !important;
        line-height: 1.7;
    }

    h1, h2, h3 { 
        color: #00ff88 !important; 
        font-weight: 800 !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }

    /* Etykiety pól - wysoki kontrast */
    .stTextInput label, .stSelectbox label, .stNumberInput label, .stSlider label {
        color: #00d4ff !important;
        font-weight: 700 !important;
        background: rgba(0,0,0,0.4);
        padding: 4px 12px;
        border-radius: 4px;
    }

    /* Metryki KPI */
    [data-testid="stMetric"] {
        background: #111111;
        border: 2px solid #00ff88;
        border-radius: 12px;
        padding: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICJALIZACJA BAZY ---
@st.cache_resource
def init_db():
    try:
