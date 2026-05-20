# modules/auth.py
"""Manejo de autenticación y sesiones"""

import streamlit as st
from config.settings import USERS


def verificar_login(usuario: str, password: str) -> bool:
    """Verifica credenciales de usuario"""
    if usuario in USERS and password == USERS[usuario]["password"]:
        st.session_state.auth = True
        st.session_state.user_role = USERS[usuario]["role"]
        st.session_state.user_name = USERS[usuario]["name"]
        return True
    return False


def login_invitado():
    """Inicia sesión como invitado"""
    st.session_state.auth = True
    st.session_state.user_role = "INVITADO"
    st.session_state.user_name = "Invitado"


def cerrar_sesion():
    """Cierra la sesión actual"""
    st.session_state.auth = False
    st.session_state.carrito = []
    st.session_state.catalogos = []
    st.session_state.stocks = []
    st.session_state.ugreen_catalogo = None


def inicializar_sesion():
    """Inicializa todas las variables de sesión"""
    if 'auth' not in st.session_state:
        st.session_state.auth = False
    if 'modo' not in st.session_state:
        st.session_state.modo = "XIAOMI"
    if 'precio_key' not in st.session_state:
        st.session_state.precio_key = "P. VIP"
    if 'catalogos' not in st.session_state:
        st.session_state.catalogos = []
    if 'stocks' not in st.session_state:
        st.session_state.stocks = []
    if 'carrito' not in st.session_state:
        st.session_state.carrito = []
    if 'ugreen_catalogo' not in st.session_state:
        st.session_state.ugreen_catalogo = None


def mostrar_pantalla_login():
    """Muestra la pantalla de login"""
    st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important; }
        .login-card { background: rgba(255,255,255,0.95); border-radius: 20px; padding: 2rem; box-shadow: 0 10px 40px rgba(0,0,0,0.2); }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        
        try:
            st.image("logo.png", width=100)
        except:
            st.markdown("<h1 style='color:#e94560; text-align:center;'>QTC</h1>", unsafe_allow_html=True)
        
        st.markdown("<h2 style='color:#1a1a2e; text-align:center;'>QTC Smart Sales Pro</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#666; text-align:center;'>Sistema Profesional de Cotización</p>", unsafe_allow_html=True)
        
        user = st.text_input("👤 Usuario", placeholder="Ingresa tu usuario")
        pw = st.text_input("🔒 Contraseña", type="password", placeholder="Ingresa tu contraseña")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🚀 Ingresar", use_container_width=True):
                if verificar_login(user, pw):
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas")
                    st.info("💡 Usuarios: admin / kimberly / vendedor | Contraseña: usuario+2026")
        with col_btn2:
            if st.button("👤 Modo invitado", use_container_width=True):
                login_invitado()
                st.rerun()
        
        st.markdown("<div class='footer'>⚡ QTC Smart Sales Pro</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
