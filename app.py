# app.py - QTC Smart Sales Pro con SIDEBAR
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
from ui.components import mostrar_header
from ui.tabs.bulk_tab import render_bulk_tab
from ui.tabs.search_tab import render_search_tab
from ui.tabs.cart_tab import render_cart_tab
from ui.tabs.skuscraper_tab import render_skuscraper_tab

# ✅ SOLO ESTOS DOS imports desde excel_utils (los que usamos en sidebar)
from utils.excel_utils import cargar_catalogo, cargar_stock
from utils.file_handlers import cargar_ugreen_catalogo


def render_sidebar():
    """Renderiza el sidebar con todas las opciones"""
    with st.sidebar:
        st.markdown("### 🎯 Configuración")
        
        # Selector de modo
        modo = st.radio(
            "📌 Marca / Modo",
            ["XIAOMI", "UGREEN", "OTRAS MARCAS"],
            index=0,
            help="XIAOMI: Lógica especial de stock\nUGREEN: Archivo específico\nOTRAS MARCAS: Lógica estándar"
        )
        st.session_state.modo = modo
        
        st.markdown("---")
        
        # Selector de precio
        precio_opcion = st.radio(
            "💰 Nivel de precio",
            ["P. VIP", "P. BOX", "P. IR"],
            index=0
        )
        st.session_state.precio_key = precio_opcion
        
        st.markdown("---")
        
        st.markdown("### 📂 Archivos")
        
        # Catálogos (solo si no es UGREEN)
        if modo != "UGREEN":
            st.markdown("**📚 Catálogos de precios**")
            archivos_cat = st.file_uploader(
                "Excel o CSV",
                type=['xlsx', 'xls', 'csv'],
                accept_multiple_files=True,
                key="cat_upload"
            )
            if archivos_cat:
                st.session_state.catalogos = []
                for archivo in archivos_cat:
                    with st.spinner(f"Cargando {archivo.name}..."):
                        cat = cargar_catalogo(archivo)
                        if cat:
                            st.session_state.catalogos.append(cat)
                            st.success(f"✅ {archivo.name[:30]}")
        
        # Catálogo UGREEN
        if modo == "UGREEN":
            st.markdown("**📚 Catálogo UGREEN**")
            archivo_ugreen = st.file_uploader(
                "Excel UGREEN (Mayor/Caja/Vip)",
                type=['xlsx', 'xls'],
                accept_multiple_files=False,
                key="ugreen_upload"
            )
            if archivo_ugreen:
                with st.spinner("Cargando UGREEN..."):
                    ugreen_cat = cargar_ugreen_catalogo(archivo_ugreen)
                    if ugreen_cat:
                        st.session_state.ugreen_catalogo = ugreen_cat
                        st.success(f"✅ UGREEN: {archivo_ugreen.name[:30]}")
        
        # Reportes de stock
        st.markdown("**📦 Reportes de stock**")
        st.caption("📌 YESSICA/APRI.004: lee 'Disponible' o 'Cantidad'")
        st.caption("📌 APRI.001: solo 'Disponible'")
        
        archivos_stock = st.file_uploader(
            "Excel",
            type=['xlsx', 'xls'],
            accept_multiple_files=True,
            key="stock_upload"
        )
        if archivos_stock:
            with st.spinner("Cargando stock..."):
                st.session_state.stocks = cargar_stock(archivos_stock, modo)
        
        st.markdown("---")
        
        # Resumen del carrito
        if st.session_state.get('carrito', []):
            st.markdown("### 🛒 Carrito")
            st.metric("Productos", len(st.session_state.carrito))
            total = sum(item.get('total', 0) for item in st.session_state.carrito)
            st.metric("Total", f"S/ {total:,.2f}")
            
            if st.button("🧹 Limpiar carrito", use_container_width=True):
                st.session_state.carrito = []
                st.rerun()
        
        st.markdown("---")
        st.caption("💡 Tips:\n- SKU:CANTIDAD para bulk\n- Buscar por SKU o descripción\n- Stock seguro: stock-2")
        
        # Botón de reinicio
        if st.button("🔄 Reiniciar todo", use_container_width=True):
            for key in ['catalogos', 'stocks', 'carrito', 'ugreen_catalogo', 'productos_actuales', 'resultados_procesados']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()


def main():
    """Función principal"""
    
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
    
    # Tabs principales
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
        f'<div class="footer">⚡ QTC Smart Sales Pro | Modo: {st.session_state.get("modo", "XIAOMI")} | '
        f'{datetime.now().strftime("%Y-%m-%d %H:%M")}</div>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
