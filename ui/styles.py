# ui/styles.py
"""CSS completo de la aplicación"""

import streamlit as st


def apply_custom_styles():
    """Aplica todos los estilos CSS personalizados"""
    st.markdown("""
    <style>
        /* FONDO DE PÁGINA - AZUL MIRAMAR VIVO */
        .stApp {
            background: linear-gradient(135deg, #0d47a1 0%, #1565c0 50%, #1e88e5 100%);
        }
        
        /* TARJETAS GLASSMORPHISM */
        .result-card, div[style*="border-radius:16px"] {
            background: rgba(30, 30, 35, 0.85) !important;
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255,255,255,0.15);
            color: #ffffff !important;
        }
        
        /* SIDEBAR - DURAZNO INTENSO */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f8a35e 0%, #e87a2d 50%, #d45a1a 100%);
            border-right: 1px solid #ffcc80;
        }
        
        [data-testid="stSidebar"] * {
            color: #ffffff !important;
        }
        
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3 {
            color: #ffffff !important;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        }
        
        /* TEXTOS GENERALES */
        .stMarkdown, .stText, .stNumberInput label, .stSelectbox label, 
        .stRadio label, .stTextInput label, .stTextArea label {
            color: #ffffff !important;
        }
        
        h1, h2, h3, h4, h5, h6,
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            color: #ffffff !important;
        }
        
        /* ALERTAS */
        div[data-testid="stAlert"][data-kind="success"] {
            background: #2e7d32 !important;
            border-left: 4px solid #1b5e20 !important;
            border-radius: 12px !important;
        }
        div[data-testid="stAlert"][data-kind="success"] .stMarkdown {
            color: #ffffff !important;
            font-weight: bold;
        }
        
        div[data-testid="stAlert"][data-kind="warning"] {
            background: #f9a825 !important;
            border-left: 4px solid #f57f17 !important;
            border-radius: 12px !important;
        }
        
        div[data-testid="stAlert"][data-kind="error"] {
            background: #d32f2f !important;
            border-left: 4px solid #b71c1c !important;
            border-radius: 12px !important;
        }
        
        /* BADGES */
        .badge-yessica { background: #4CAF50; color: white !important; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; display: inline-block; margin: 2px; }
        .badge-apri004 { background: #FF9800; color: white !important; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; display: inline-block; margin: 2px; }
        .badge-apri001 { background: #f44336; color: white !important; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; display: inline-block; margin: 2px; }
        .badge-warning { background: #ff9800; color: white !important; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; display: inline-block; }
        .badge-ugreen { background: #00BCD4; color: white !important; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; display: inline-block; margin: 2px; }
        
        /* FOOTER */
        .footer {
            text-align: center;
            padding: 1rem;
            color: rgba(255,255,255,0.7) !important;
            font-size: 0.7rem;
            border-top: 1px solid rgba(255,255,255,0.2);
            margin-top: 2rem;
        }
        
        /* CORRECCIÓN DE COLORES EN TARJETAS BLANCAS */
        div[style*="border-radius:16px"] *,
        div[style*="background:#FFEBEE"] *,
        div[style*="background:#E3F2FD"] *,
        div[style*="background:#F5F5F5"] * {
            color: #1a1a2e !important;
        }
        
        div[style*="border-radius:16px"][style*="margin-bottom:1rem"] {
            background: #ffffff !important;
        }
        
        .badge-yessica, .badge-apri004, .badge-apri001, .badge-warning, .badge-ugreen,
        .badge-yessica *, .badge-apri004 *, .badge-apri001 *, .badge-warning *, .badge-ugreen * {
            color: white !important;
        }
    </style>
    """, unsafe_allow_html=True)
