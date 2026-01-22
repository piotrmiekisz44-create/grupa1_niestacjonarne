# --- KONFIGURACJA WIZUALNA I CSS (Zoptymalizowana pod czytelność) ---
st.set_page_config(
    page_title="Logistics Intelligence Terminal", 
    page_icon="🚛", 
    layout="wide"
)

st.markdown("""
    <style>
    /* 1. Główne tło z obrazem logistycznym */
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
        url("https://images.unsplash.com/photo-1494412519320-aa613dfb7738?q=80&w=2070");
        background-attachment: fixed;
        background-size: cover;
    }

    /* 2. LEWE MENU (Sidebar) - Ciemniejszy, głęboki kolor */
    [data-testid="stSidebar"] {
        background-color: #050505 !important; /* Głęboka czerń dla kontrastu */
        border-right: 1px solid #00ff88;
    }
    
    /* 3. CZYTELNOŚĆ TEKSTU I CZCIONEK */
    html, body, [class*="st-"] {
        font-family: 'Inter', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        color: #FFFFFF !important;
        font-size: 1.05rem; /* Delikatnie większa czcionka */
        line-height: 1.6; /* Większe odstępy między
