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

# --- STYLIZACJA CSS (CZARNE CZCIONKI I JASNA CZYTELNOŚĆ) ---
st.markdown("""
    <style>
    /* Tło i główny kontener - rozjaśnione tło obrazka dla kontrastu */
    .stApp {
        background-image: linear-gradient(rgba(255,255,255,0.8), rgba(255,255,255,0.8)), 
        url("https://images.unsplash.com/photo-1494412519320-aa613dfb7738?q=80&w=2070");
        background-attachment: fixed;
        background-size: cover;
    }

    /* Panele i kontenery - jasne kolory tła */
    [data-testid="stSidebar"] {
        background-color: #f1f3f6 !important;
        border-right: 3px solid #00ff88;
    }
    
    .main .block-container {
        background-color: rgba(255, 255, 255, 0.96);
        padding: 40px;
        border-radius: 20px;
        border: 1px solid #dee2e6;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }

    /* GLOBALNE WYMUSZENIE CZARNEJ CZCIONKI */
    html, body, [class*="st-"], .stMarkdown p, label, .stMetric div, h1, h2, h3 {
        font-family: 'Segoe UI', Roboto, sans-serif;
        color: #000000 !important;
    }

    h1, h2, h3 { 
        color: #000000 !important; 
        text-transform: uppercase;
        font-weight: 800;
    }

    /* Stylizacja pól tekstowych, list rozwijanych i liczbowych */
    input, textarea, select, div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #00ff88 !important;
        border
