# ui/components.py
import streamlit as st
from utils.excel_utils import cargar_catalogo, cargar_stock
from utils.file_handlers import cargar_ugreen_catalogo
from utils.formatters import construir_badge_stock, formatear_precio


def mostrar_header(user_name: str, user_role: str):
    """Muestra el header de la aplicación"""
    col1, col2, col3 = st.columns([1, 5, 2])
    
    with col1:
        try:
            st.image("logo.png", width=60)
        except:
            st.markdown("**QTC**", unsafe_allow_html=True)
    
    with col2:
        st.markdown("# QTC Smart Sales Pro")
        st.caption("Sistema Profesional de Cotización | Soporte XIAOMI · UGREEN · OTRAS MARCAS")
    
    with col3:
        role_badge = {"ADMIN": "🔧", "KAM": "⭐", "VENDEDOR": "🛒", "INVITADO": "👤"}
        badge = role_badge.get(user_role, "👤")
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.1); padding: 0.5rem 1rem; border-radius: 12px; text-align: right;">
            <span>{badge} {user_name}</span><br>
            <span style="font-size: 0.7rem;">{user_role}</span>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 Cerrar Sesión", key="logout"):
            return False
    return True


def render_sidebar():
    """Renderiza el sidebar con todas las opciones"""
    with st.sidebar:
        st.markdown("### 🎯 Configuración")
        
        # Selector de modo
        modo = st.radio(
            "📌 Marca / Modo",
            ["XIAOMI", "UGREEN", "OTRAS MARCAS"],
            index=0,
            help="XIAOMI: Stock YESSICA/APRI.004/APRI.001\nUGREEN: Catálogo específico"
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
        
        # Catálogos (XIAOMI/OTROS)
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
                "Excel UGREEN",
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
        st.caption("📌 YESSICA/APRI.004: stock inmediato | APRI.001: stock remoto")
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
        st.caption("💡 Tips:\n- Formato: SKU:CANTIDAD\n- Buscar por SKU o descripción\n- APRI.001 = última opción")
        
        # Botón de reinicio
        if st.button("🔄 Reiniciar todo", use_container_width=True):
            for key in ['catalogos', 'stocks', 'carrito', 'ugreen_catalogo', 'resultados_bulk']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
