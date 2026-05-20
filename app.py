# app.py - QTC Smart Sales Pro v5.0 (Modular)
"""Punto de entrada principal de la aplicación"""

import streamlit as st
from datetime import datetime

# Configuración de página (DEBE SER LO PRIMERO)
from config.settings import PAGE_CONFIG
st.set_page_config(**PAGE_CONFIG)

# Importaciones modulares
from modules.auth import inicializar_sesion, mostrar_pantalla_login, cerrar_sesion
from ui.styles import apply_custom_styles
from ui.components import mostrar_header
# app.py - Al inicio con los otros imports
from ui.tabs.bulk_tab import render_bulk_tab
from ui.tabs.search_tab import render_search_tab
from ui.tabs.cart_tab import render_cart_tab
from ui.tabs.skuscraper_tab import render_skuscraper_tab  # NUEVO


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
    
    # Mostrar header
    if not mostrar_header(st.session_state.user_name, st.session_state.user_role):
        cerrar_sesion()
        st.rerun()
        return
    
    st.markdown("---")
    
    # app.py - Sección de tabs (reemplazar la existente)

# Tabs principales (AHORA CON 4 TABS)
tab1, tab2, tab3, tab4 = st.tabs([
    "📦 MODO MASIVO (Bulk)", 
    "🔍 BÚSQUEDA INTELIGENTE", 
    "🛒 CARRITO DE COTIZACIÓN",
    "🔧 SKU SCRAPER"  # NUEVO TAB
])

with tab1:
    render_bulk_tab()

with tab2:
    render_search_tab()

with tab3:
    render_cart_tab()

with tab4:
    from ui.tabs.skuscraper_tab import render_skuscraper_tab
    render_skuscraper_tab()
    
    # Footer
    st.markdown("---")
    st.markdown(
        f'<div class="footer">⚡ QTC Smart Sales Pro v5.0 | Modo: {st.session_state.modo} | '
        f'YESSICA/APRI.004: stock-2 | APRI.001: 15% máx 100 | {datetime.now().strftime("%Y-%m-%d %H:%M")}</div>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
