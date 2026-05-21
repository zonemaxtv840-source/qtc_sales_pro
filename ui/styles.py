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
        }
        [data-testid="stSidebar"] * {
            color: #ffffff !important;
        }
        
        /* TEXTOS GENERALES */
        .stMarkdown, .stText, .stNumberInput label, .stSelectbox label {
            color: #ffffff !important;
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: #ffffff !important;
        }
        
        /* ========== CARDS BLANCAS CON TEXTO OSCURO ========== */
        /* Para cards con fondo blanco */
        div[style*="background:white"],
        div[style*="background:#ffffff"],
        div[style*="background:#fff"],
        div[style*="background-color:white"],
        div[style*="background-color:#ffffff"] {
            color: #1a1a2e !important;
        }
        
        div[style*="background:white"] *,
        div[style*="background:#ffffff"] *,
        div[style*="background:#fff"] * {
            color: #1a1a2e !important;
        }
        
        /* Cards con bordes de colores */
        div[style*="border-left:5px solid"] {
            background: white !important;
        }
        
        div[style*="border-left:5px solid"] * {
            color: #1a1a2e !important;
        }
        
        /* Badges dentro de cards - mantener blanco */
        div[style*="background:white"] span[style*="background"],
        div[style*="background:#ffffff"] span[style*="background"],
        div[style*="border-left:5px solid"] span[style*="background"] {
            color: white !important;
        }
        
        /* Títulos dentro de cards */
        div[style*="background:white"] strong,
        div[style*="background:#ffffff"] strong {
            color: #1a1a2e !important;
        }
        
        /* FOOTER */
        .footer {
            text-align: center;
            padding: 1rem;
            color: rgba(255,255,255,0.7);
            font-size: 0.7rem;
            border-top: 1px solid rgba(255,255,255,0.2);
            margin-top: 2rem;
        }
        
        /* BADGES */
        .badge-yessica { background: #4CAF50; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; display: inline-block; margin: 2px; }
        .badge-apri004 { background: #FF9800; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; display: inline-block; margin: 2px; }
        .badge-apri001 { background: #f44336; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; display: inline-block; margin: 2px; }
        .badge-ugreen { background: #00BCD4; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; display: inline-block; margin: 2px; }
        
        /* DATA FRAMES */
        .stDataFrame {
            background: white;
            border-radius: 12px;
            padding: 0.5rem;
        }
        .stDataFrame * {
            color: #1a1a2e !important;
        }
        
        /* INFO BOXES */
        .stAlert {
            border-radius: 12px !important;
        }
        
        /* CODE BLOCKS */
        code {
            background: #f0f0f0 !important;
            color: #d63384 !important;
            padding: 2px 6px !important;
            border-radius: 6px !important;
        }
    </style>
    """, unsafe_allow_html=True)
