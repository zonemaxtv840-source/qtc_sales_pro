# ui/styles.py
import streamlit as st

def apply_custom_styles():
    st.markdown("""
    <style>
        /* FONDO DE PÁGINA */
        .stApp {
            background: linear-gradient(135deg, #0d47a1 0%, #1565c0 50%, #1e88e5 100%);
        }
        
        /* SIDEBAR */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f8a35e 0%, #e87a2d 50%, #d45a1a 100%);
            border-right: 1px solid #ffcc80;
        }
        [data-testid="stSidebar"] * {
            color: #ffffff !important;
        }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
            color: #ffffff !important;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        }
        
        /* TEXTOS GENERALES */
        .stMarkdown, .stText, .stNumberInput label, .stSelectbox label,
        .stRadio label, .stTextInput label {
            color: #ffffff !important;
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: #ffffff !important;
        }
        
        /* TARJETAS BLANCAS - FORZAR TEXTO OSCURO */
        div[style*="background:white"],
        div[style*="background:#ffffff"],
        div[style*="background:#fff"],
        div[style*="border-radius:12px"][style*="border-left"],
        div[class*="card"] {
            color: #1a1a2e !important;
        }
        
        div[style*="background:white"] *,
        div[style*="background:#ffffff"] *,
        div[style*="border-radius:12px"] * {
            color: #1a1a2e !important;
        }
        
        /* Badges - mantener texto blanco */
        span[style*="background"] {
            color: white !important;
        }
        
        /* ALERTAS */
        div[data-testid="stAlert"][data-kind="success"] {
            background: #2e7d32 !important;
            border-radius: 12px !important;
        }
        div[data-testid="stAlert"][data-kind="warning"] {
            background: #f9a825 !important;
            border-radius: 12px !important;
        }
        div[data-testid="stAlert"][data-kind="error"] {
            background: #d32f2f !important;
            border-radius: 12px !important;
        }
        div[data-testid="stAlert"][data-kind="info"] {
            background: #0288d1 !important;
            border-radius: 12px !important;
        }
        
        /* BADGES */
        .badge-yessica { background: #4CAF50; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; display: inline-block; margin: 2px; }
        .badge-apri004 { background: #FF9800; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; display: inline-block; margin: 2px; }
        .badge-apri001 { background: #f44336; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; display: inline-block; margin: 2px; }
        .badge-ugreen { background: #00BCD4; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; display: inline-block; margin: 2px; }
        
        /* FOOTER */
        .footer {
            text-align: center;
            padding: 1rem;
            color: rgba(255,255,255,0.6);
            font-size: 0.7rem;
            border-top: 1px solid rgba(255,255,255,0.1);
            margin-top: 2rem;
        }
        
        /* DATA FRAMES */
        .stDataFrame {
            background: white;
            border-radius: 12px;
            padding: 0.5rem;
        }
        .stDataFrame * {
            color: #1a1a2e !important;
        }
        
        /* SCROLLBAR */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
    </style>
    """, unsafe_allow_html=True)
