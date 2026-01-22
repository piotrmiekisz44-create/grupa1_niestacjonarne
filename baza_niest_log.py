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

# --- STYLIZACJA CSS (WYSOKI KONTRAST I CZYTELNOŚĆ) ---
st.markdown("""
    <style>
    /* Tło aplikacji */
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), 
        url("https://images.unsplash.com/photo-1494412519320-aa613dfb7738?q=80&w=2070");
        background-attachment: fixed;
        background-size: cover;
    }

    /* GŁÓWNY KONTENER TREŚCI */
    .main .block-container {
        background-color: rgba(20, 20, 20, 0.95);
        padding: 40px;
        border-radius: 15px;
        border: 1px solid #00ff88;
    }

    /* POLA TEKSTOWE I INPUT
