import streamlit as st
from modules.auth import inicializar_sesion, mostrar_login
from modules.ui_components import aplicar_estilos_globales
from modules.data_loader import cargar_catalogo, cargar_stock_completo

# Configuración de página (DEBE SER PRIMERO)
st.set_page_config(
    page_title="QTC SMART SALES PRO",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar
inicializar_sesion()
aplicar_estilos_globales()

# Carga de datos en sidebar (visible antes de login)
with st.sidebar:
    st.markdown("## 📁 DATOS")
    
    catalogo_file = st.file_uploader("📊 Catálogo de precios", type=["xlsx", "csv"])
    stock_file = st.file_uploader("📦 Archivo de stock", type=["xlsx"])
    
    if catalogo_file and stock_file:
        with st.spinner("Cargando datos..."):
            st.session_state.catalogo = cargar_catalogo(catalogo_file)
            st.session_state.stock = cargar_stock_completo(stock_file)
            if st.session_state.catalogo is not None:
                st.success(f"✅ {len(st.session_state.catalogo)} productos cargados")
            if st.session_state.stock:
                total_items = sum(len(df) for df in st.session_state.stock.values())
                st.success(f"✅ {total_items} registros de stock")

# Login
if not st.session_state.autenticado:
    mostrar_login()
else:
    # Sidebar con info del usuario
    with st.sidebar:
        st.divider()
        st.markdown(f"### 👤 {st.session_state.usuario.upper()}")
        if st.button("🚪 Cerrar sesión", use_container_width=True):
            st.session_state.autenticado = False
            st.session_state.carrito = []
            st.rerun()
    
    # Verificar que hay datos cargados
    if st.session_state.get("catalogo") is None or st.session_state.get("stock") is None:
        st.warning("⚠️ Por favor carga los archivos de catálogo y stock en el panel izquierdo")
        st.stop()
    
    # Importar y mostrar páginas
    from pages import (01_masivo, 02_busqueda_inteligente, 
                       03_carrito, 04_sku_scraper)
    
    # Menú principal con tabs más profesionales
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h1>🏢 QTC SMART SALES PRO</h1>
        <p style="color: #aaa;">Sistema profesional de cotizaciones</p>
    </div>
    """, unsafe_allow_html=True)
    
    tabs = st.tabs(["📦 MODO MASIVO", "🔍 BÚSQUEDA INTELIGENTE", "🛒 CARRITO", "🔧 SKU SCRAPER"])
    
    with tabs[0]:
        01_masivo.mostrar()
    with tabs[1]:
        02_busqueda_inteligente.mostrar()
    with tabs[2]:
        03_carrito.mostrar()
    with tabs[3]:
        04_sku_scraper.mostrar()
