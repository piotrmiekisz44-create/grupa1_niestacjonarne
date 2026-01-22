import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

# --- KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="LOG-PRO: System Logistyczny", 
    page_icon="🚢", 
    layout="wide"
)

# --- WYSOKI KONTRAST I CZYTELNOŚĆ (CSS) ---
st.markdown("""
    <style>
    /* Tło główne z obrazem branżowym */
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), 
        url("https://images.unsplash.com/photo-1494412519320-aa613dfb7738?q=80&w=2070");
        background-attachment: fixed;
        background-size: cover;
    }

    /* LEWE MENU (Sidebar) - Głęboka czerń dla kontrastu */
    [data-testid="stSidebar"] {
        background-color: #050505 !important;
        border-right: 2px solid #00ff88;
    }
    
    /* GŁÓWNY PANEL - Bardzo ciemny dla czytelności tekstu */
    .main .block-container {
        background-color: rgba(0, 0, 0, 0.92);
        padding: 40px;
        border-radius: 20px;
        border: 1px solid rgba(0, 212, 255, 0.3);
    }

    /* PRZEJRZYSTE CZCIONKI */
    html, body, [class*="st-"] {
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        color: #FFFFFF !important;
        font-size: 1.05rem;
        line-height: 1.6;
    }

    h1, h2, h3 { 
        color: #00ff88 !important; 
        font-weight: 800 !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }

    /* Stylizacja pól formularza (Etykiety) */
    .stTextInput label, .stSelectbox label, .stNumberInput label, .stSlider label {
        color: #00d4ff !important;
        font-weight: 700 !important;
