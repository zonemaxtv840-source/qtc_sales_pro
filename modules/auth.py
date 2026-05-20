# modules/auth.py
import streamlit as st

USERS = {
    "admin": {"password": "qtc2026", "role": "ADMIN", "name": "Administrador"},
    "kimberly": {"password": "kam2026", "role": "KAM", "name": "Kimberly"},
    "vendedor": {"password": "ventas2026", "role": "VENDEDOR", "name": "Vendedor"}
}


def inicializar_sesion():
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
    if 'user_role' not in st.session_state:
        st.session_state.user_role = "INVITADO"
    if 'user_name' not in st.session_state:
        st.session_state.user_name = "Invitado"


def verificar_login(usuario: str, password: str) -> bool:
    if usuario in USERS and password == USERS[usuario]["password"]:
        st.session_state.auth = True
        st.session_state.user_role = USERS[usuario]["role"]
        st.session_state.user_name = USERS[usuario]["name"]
        return True
    return False


def login_invitado():
    st.session_state.auth = True
    st.session_state.user_role = "INVITADO"
    st.session_state.user_name = "Invitado"


def cerrar_sesion():
    st.session_state.auth = False
    st.session_state.carrito = []


def mostrar_pantalla_login():
    st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important; }
        .login-card { background: rgba(255,255,255,0.95); border-radius: 20px; padding: 2rem; }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown("<h1 style='text-align:center;'>QTC Smart Sales Pro</h1>", unsafe_allow_html=True)
        
        user = st.text_input("👤 Usuario", placeholder="admin / kimberly / vendedor")
        pw = st.text_input("🔒 Contraseña", type="password")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🚀 Ingresar", use_container_width=True):
                if verificar_login(user, pw):
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas")
        with col_btn2:
            if st.button("👤 Invitado", use_container_width=True):
                login_invitado()
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
