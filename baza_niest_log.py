import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

# --- KONFIGURACJA STRONY I CZYTELNOŚCI ---
st.set_page_config(
    page_title="LOG-PRO: Logistics Intelligence Terminal", 
    page_icon="🚛", 
    layout="wide"
)

# --- STYLIZACJA CSS (CIEMNY SIDEBAR I WYRAŹNY TEKST) ---
st.markdown("""
    <style>
    /* Tło z branży transportowej */
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.75)), 
        url("https://images.unsplash.com/photo-1494412519320-aa613dfb7738?q=80&w=2070");
        background-attachment: fixed;
        background-size: cover;
    }

    /* LEWE MENU - Głęboka czerń dla maksymalnego kontrastu */
    [data-testid="stSidebar"] {
        background-color: #050505 !important;
        border-right: 2px solid #00ff88;
    }
    
    /* GŁÓWNY PANEL - Bardzo ciemny dla czytelności tekstu */
    .main .block-container {
        background-color: rgba(0, 0, 0, 0.9);
        padding: 50px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-top: 20px;
    }

    /* CZYTELNOŚĆ CZCIONEK I INTERLINIA */
    html, body, [class*="st-"] {
        font-family: 'Segoe UI', Roboto, Helvetica, sans-serif;
        color: #FFFFFF !important;
        line-height: 1.7; /* Przejrzyste odstępy między liniami */
    }

    h
