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

# --- STYLIZACJA CSS (WYSOKI KONTRAST I CZYTELNOŚĆ) ---
st.markdown("""
    <style>
    /* Tło branżowe: Port kontenerowy */
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), 
        url("https://images.unsplash.com/photo-1494412519320-aa613dfb7738?q=80&w=2070");
        background-attachment: fixed;
        background-size: cover;
    }

    /* LEWE MENU - Głęboka czerń dla kontrastu */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 3px solid #00ff88;
    }
    
    /* GŁÓWNY PANEL */
    .main .block-container {
        background-color: rgba(10, 10, 10, 0.95);
        padding: 50px;
        border-radius: 20px;
        border: 1px solid #00ff88;
        margin-top: 20px;
    }

    /* --- KLUCZOWE ZMIANY DLA WIDOCZNOŚCI TEKSTU --- */
    
    /* Wszystkie teksty w aplikacji - czysta biel */
    html, body, [class*="st-"], .stMarkdown p, .stText {
        color: #FFFFFF !important;
        font-weight: 500;
        font-size: 1.05rem;
    }

    /* Nagłówki - jaskrawy zielony */
    h1, h2, h3 { 
        color: #00ff88 !important; 
        font-weight: 850 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }

    /* Etykiety pól (Labels) - jaskrawy błękit na ciemnym tle */
    label, [data-testid="stWidgetLabel"] p {
        color: #00d4ff !important;
        font-weight: 800 !important;
        font-size: 1.
