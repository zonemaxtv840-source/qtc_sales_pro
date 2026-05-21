# app.py - QTC Smart Sales Pro v5.0 (Versión Mejorada)
import streamlit as st
from datetime import datetime

# Configuración de página (DEBE SER LO PRIMERO)
st.set_page_config(
    page_title="QTC Smart Sales Pro",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Importaciones modulares
from modules.auth import inicializar_sesion, mostrar_pantalla_login, cerrar_sesion
from ui.styles import apply_custom_styles
from ui.components import mostrar_header, render_sidebar
from ui.tabs.bulk_tab import render_bulk_tab
from ui.tabs.search_tab import render_search_tab
from ui.tabs.cart_tab import render_cart_tab
from ui.tabs.skuscraper_tab import render_skuscraper_tab


def main():
    """Función principal de la aplicación"""
    
    # Aplicar estilos CSS
    apply_custom_styles()
    
    # Inicializar sesión
    inicializar_sesion()
    
    # Verificar autenticación
    if not st.session_state.auth:
        mostrar_pantalla_login()
        return
    
    # Renderizar sidebar
    render_sidebar()
    
    # Mostrar header
    if not mostrar_header(st.session_state.user_name, st.session_state.user_role):
        cerrar_sesion()
        st.rerun()
        return
    
    st.markdown("---")
    
    # 4 Tabs principales
    tab1, tab2, tab3, tab4 = st.tabs([
        "📦 MODO MASIVO (Bulk)", 
        "🔍 BÚSQUEDA INTELIGENTE", 
        "🛒 CARRITO DE COTIZACIÓN",
        "🔧 SKU SCRAPER"
    ])
    
    with tab1:
        render_bulk_tab()
    
    with tab2:
        render_search_tab()
    
    with tab3:
        render_cart_tab()
    
    with tab4:
        render_skuscraper_tab()
    
    # Footer
    st.markdown("---")
    st.markdown(
        f'<div class="footer">⚡ QTC Smart Sales Pro v5.0 | Modo: {st.session_state.get("modo", "XIAOMI")} | '
        f'{datetime.now().strftime("%Y-%m-%d %H:%M")}</div>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
