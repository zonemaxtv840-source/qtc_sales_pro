# ui/styles.py
import streamlit as st

def apply_custom_styles():
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #0d47a1 0%, #1565c0 50%, #1e88e5 100%);
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f8a35e 0%, #e87a2d 50%, #d45a1a 100%);
        }
        [data-testid="stSidebar"] * {
            color: #ffffff !important;
        }
        .stMarkdown, .stText, .stNumberInput label {
            color: #ffffff !important;
        }
        h1, h2, h3 {
            color: #ffffff !important;
        }
        .footer {
            text-align: center;
            padding: 1rem;
            color: rgba(255,255,255,0.7);
            font-size: 0.7rem;
        }
        .badge-yessica { background: #4CAF50; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; }
        .badge-apri004 { background: #FF9800; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; }
        .badge-apri001 { background: #f44336; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; }
        .badge-ugreen { background: #00BCD4; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; }
    </style>
    """, unsafe_allow_html=True)
