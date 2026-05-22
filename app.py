import streamlit as st
from modules.auth import inicializar_sesion, mostrar_login
from modules.ui_components import aplicar_estilos_globales

# Configuración de página
st.set_page_config(
    page_title="QTC SMART SALES PRO",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar
inicializar_sesion()
aplicar_estilos_globales()

# Login
if not st.session_state.autenticado:
    mostrar_login()
else:
    # Sidebar con info del usuario
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.usuario.upper()}")
        if st.button("🚪 Cerrar sesión"):
            st.session_state.autenticado = False
            st.session_state.carrito = []
            st.rerun()
    
    # Importar y mostrar páginas
    from pages import (01_masivo, 02_busqueda_inteligente, 
                       03_carrito, 04_sku_scraper)
    
    # Menú principal
    tabs = st.tabs(["📦 MODO MASIVO", "🔍 BÚSQUEDA INTELIGENTE", 
                    "🛒 CARRITO", "🔧 SKU SCRAPER"])
    
    with tabs[0]:
        01_masivo.mostrar()
    with tabs[1]:
        02_busqueda_inteligente.mostrar()
    with tabs[2]:
        03_carrito.mostrar()
    with tabs[3]:
        04_sku_scraper.mostrar()
