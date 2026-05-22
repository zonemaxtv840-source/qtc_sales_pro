import streamlit as st
from utils.constants import ROLES

def autenticar_usuario(usuario, password):
    """Verifica credenciales"""
    if usuario in ROLES:
        if ROLES[usuario]["password"] == password:
            return usuario
    return None

def inicializar_sesion():
    """Inicializa variables de sesión"""
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    if "usuario" not in st.session_state:
        st.session_state.usuario = None
    if "rol" not in st.session_state:
        st.session_state.rol = None
    if "carrito" not in st.session_state:
        st.session_state.carrito = []
    if "ultima_busqueda" not in st.session_state:
        st.session_state.ultima_busqueda = []

def mostrar_login():
    """Muestra formulario de login"""
    st.markdown("""
    <style>
    .login-container {
        max-width: 400px;
        margin: 100px auto;
        padding: 40px;
        background: white;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.image("logo.png", width=200) if st.session_state.get("logo_cargado") else st.markdown("## 🏢 QTC")
            st.markdown("### SMART SALES PRO")
            
            usuario = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            
            if st.button("Ingresar", use_container_width=True):
                user = autenticar_usuario(usuario, password)
                if user:
                    st.session_state.autenticado = True
                    st.session_state.usuario = usuario
                    st.session_state.rol = usuario
                    st.rerun()
                else:
                    st.error("❌ Credenciales inválidas")
