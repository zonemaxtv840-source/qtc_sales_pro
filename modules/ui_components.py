# modules/ui_components.py
# Componentes de interfaz de usuario (CSS, badges, header, footer)

import streamlit as st
from datetime import datetime
from utils.constants import COLORES_BADGES

def aplicar_estilos_globales():
    """Aplica CSS global a la aplicación"""
    st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #0d47a1 0%, #1565c0 50%, #1e88e5 100%); }
        [data-testid="stSidebar"] { background: linear-gradient(180deg, #f8a35e 0%, #e87a2d 50%, #d45a1a 100%); border-right: 1px solid #ffcc80; }
        [data-testid="stSidebar"] * { color: #ffffff !important; }
        .stMarkdown, .stText, .stNumberInput label, .stSelectbox label { color: #ffffff !important; }
        h1, h2, h3 { color: #ffffff !important; }
        div[style*="background:white"] * { color: #1a1a2e !important; }
        
        .badge-yessica { background: #4CAF50; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; display: inline-block; margin: 2px; }
        .badge-apri004 { background: #FF9800; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; display: inline-block; margin: 2px; }
        .badge-apri001 { background: #f44336; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; display: inline-block; margin: 2px; }
        .badge-ugreen { background: #00BCD4; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; display: inline-block; margin: 2px; }
        
        .counter-summary { background: rgba(0,0,0,0.3); border-radius: 12px; padding: 1rem; margin-bottom: 1rem; display: flex; justify-content: space-around; flex-wrap: wrap; }
        .counter-item { text-align: center; padding: 0.5rem; }
        
        .footer { text-align: center; padding: 1rem; color: rgba(255,255,255,0.7); font-size: 0.7rem; border-top: 1px solid rgba(255,255,255,0.2); margin-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

def construir_badge_stock(stock_yessica: int, stock_apri004: int, stock_apri001: int) -> str:
    """Construye badges para los 3 almacenes"""
    return f"""
    <div style="display:flex; flex-wrap:wrap; gap:8px; margin:8px 0;">
        <span class="badge-yessica">🟢 YESSICA: {stock_yessica}</span>
        <span class="badge-apri004">🟡 APRI.004: {stock_apri004}</span>
        <span class="badge-apri001">🔴 APRI.001: {stock_apri001}</span>
    </div>
    """

def badge_ugreen(stock: int) -> str:
    """Badge para UGREEN"""
    return f'<span class="badge-ugreen">📦 UGREEN: {stock}</span>'

def restaurar_sidebar():
    """Restaura el sidebar después del login"""
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: block; }
    </style>
    """, unsafe_allow_html=True)

def mostrar_header():
    """Muestra el header con información del usuario"""
    col1, col2, col3 = st.columns([1, 5, 2])
    with col1:
        try:
            st.image("logo.png", width=60)
        except:
            st.markdown("**QTC**", unsafe_allow_html=True)
    with col2:
        st.markdown("# QTC Smart Sales Pro")
        st.caption("Sistema Profesional de Cotización | Soporte XIAOMI · UGREEN")
    with col3:
        role_badge = {"ADMIN": "🔧", "KAM": "⭐", "VENDEDOR": "🛒", "INVITADO": "👤"}
        badge = role_badge.get(st.session_state.user_role, "👤")
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.1); padding: 0.5rem 1rem; border-radius: 12px; text-align: right;">
            <span>{badge} {st.session_state.user_name}</span><br>
            <span style="font-size: 0.7rem;">{st.session_state.user_role}</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚪 Cerrar Sesión", key="logout"):
            st.session_state.auth = False
            st.session_state.carrito = []
            st.rerun()
    st.markdown("---")

def mostrar_footer(modo: str):
    """Muestra el footer"""
    st.markdown("---")
    st.markdown(f'<div class="footer">⚡ QTC Smart Sales Pro v5.0 (Modular) | Modo: {modo} | YESSICA/APRI.004: stock inmediato | APRI.001: stock remoto | {datetime.now().strftime("%Y-%m-%d %H:%M")}</div>', unsafe_allow_html=True)
def badge_ugreen(stock: int) -> str:
    """Badge para UGREEN"""
    if stock > 0:
        return f'<span class="badge-ugreen">📦 UGREEN: {stock}</span>'
    return '<span class="badge-ugreen">❌ UGREEN: Sin stock</span>'
