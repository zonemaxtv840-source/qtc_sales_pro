# modules/auth.py
# Autenticación y gestión de sesiones

import streamlit as st
from utils.constants import ROLES

def autenticar_usuario(usuario: str, password: str) -> dict:
    """Verifica credenciales y retorna datos del usuario"""
    if usuario in ROLES and password == ROLES[usuario]["password"]:
        return {
            "autenticado": True,
            "usuario": usuario,
            "rol": ROLES[usuario]["rol"],
            "nombre": ROLES[usuario]["nombre"]
        }
    return {"autenticado": False}

def inicializar_sesion():
    """Inicializa todas las variables de sesión"""
    if "auth" not in st.session_state:
        st.session_state.auth = False
    if "modo" not in st.session_state:
        st.session_state.modo = "XIAOMI"
    if "precio_key" not in st.session_state:
        st.session_state.precio_key = "P. VIP"
    if "catalogos" not in st.session_state:
        st.session_state.catalogos = []
    if "stocks" not in st.session_state:
        st.session_state.stocks = []
    if "carrito" not in st.session_state:
        st.session_state.carrito = []
    if "ugreen_catalogo" not in st.session_state:
        st.session_state.ugreen_catalogo = None
    if "resultados_bulk" not in st.session_state:
        st.session_state.resultados_bulk = []
    if "user_role" not in st.session_state:
        st.session_state.user_role = None
    if "user_name" not in st.session_state:
        st.session_state.user_name = None
    if "usuario" not in st.session_state:
        st.session_state.usuario = None

def mostrar_login():
    """Muestra pantalla de login"""
    # Ocultar sidebar durante login
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none; }
        .stApp { margin-left: 0; }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div style="background:rgba(255,255,255,0.95);border-radius:20px;padding:2rem;margin-top:50px;">', unsafe_allow_html=True)
        
        try:
            st.image("logo.png", width=100)
        except:
            st.markdown("<h1 style='color:#e94560;text-align:center;'>QTC</h1>", unsafe_allow_html=True)
        
        st.markdown("<h2 style='color:#1a1a2e;text-align:center;'>QTC Smart Sales Pro</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#666;text-align:center;'>Sistema Profesional de Cotización</p>", unsafe_allow_html=True)
        
        usuario = st.text_input("👤 Usuario", placeholder="admin / kimberly / vendedor")
        password = st.text_input("🔒 Contraseña", type="password")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🚀 Ingresar", use_container_width=True):
                resultado = autenticar_usuario(usuario, password)
                if resultado["autenticado"]:
                    st.session_state.auth = True
                    st.session_state.user_role = resultado["rol"]
                    st.session_state.user_name = resultado["nombre"]
                    st.session_state.usuario = usuario
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas")
        with col_btn2:
            if st.button("👤 Invitado", use_container_width=True):
                st.session_state.auth = True
                st.session_state.user_role = "INVITADO"
                st.session_state.user_name = "Invitado"
                st.session_state.usuario = "invitado"
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
