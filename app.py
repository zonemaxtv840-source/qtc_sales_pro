# app.py - QTC Smart Sales Pro v5.0 (MODULAR)

import streamlit as st
from modules.auth import inicializar_sesion, mostrar_login
from modules.ui_components import (
    aplicar_estilos_globales, restaurar_sidebar, 
    mostrar_header, mostrar_footer
)
from modules.data_loader import cargar_catalogo, cargar_stock, cargar_ugreen_catalogo
from modules.stock_engine import buscar_stock_para_sku, buscar_producto, buscar_ugreen_producto

# Configuración de página
st.set_page_config(
    page_title="QTC Smart Sales Pro",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inicializar
inicializar_sesion()
aplicar_estilos_globales()

# Login
if not st.session_state.auth:
    mostrar_login()
    st.stop()

# Restaurar sidebar después del login
restaurar_sidebar()

# Header
mostrar_header()

# ============================================
# SIDEBAR - CARGA DE ARCHIVOS
# ============================================

with st.sidebar:
    st.markdown("### 🎯 Configuración")
    
    marca_seleccionada = st.radio(
        "📌 Marca / Modo",
        ["XIAOMI", "UGREEN", "OTRAS MARCAS"],
        index=0 if st.session_state.modo == "XIAOMI" else 1,
        help="XIAOMI: Stock YESSICA/APRI.004/APRI.001\nUGREEN: Catálogo específico"
    )
    st.session_state.modo = marca_seleccionada
    
    st.markdown("---")
    
    precio_opcion = st.radio(
        "💰 Nivel de precio",
        ["P. VIP", "P. BOX", "P. IR"],
        index=0
    )
    st.session_state.precio_key = precio_opcion
    
    st.markdown("---")
    
    st.markdown("### 📂 Archivos")
    
    if marca_seleccionada != "UGREEN":
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
                cat = cargar_catalogo(archivo)
                if cat:
                    st.session_state.catalogos.append(cat)
                    st.success(f"✅ {archivo.name[:30]}")
    
    if marca_seleccionada == "UGREEN":
        st.markdown("**📚 Catálogo UGREEN**")
        archivo_ugreen = st.file_uploader(
            "Excel UGREEN",
            type=['xlsx', 'xls'],
            accept_multiple_files=False,
            key="ugreen_upload"
        )
        if archivo_ugreen:
            ugreen_cat = cargar_ugreen_catalogo(archivo_ugreen)
            if ugreen_cat:
                st.session_state.ugreen_catalogo = ugreen_cat
                st.success(f"✅ UGREEN: {archivo_ugreen.name[:30]}")
    
    st.markdown("**📦 Reportes de stock**")
    st.caption("📌 APRI.001 usa columna 'Disponible'")
    archivos_stock = st.file_uploader(
        "Excel",
        type=['xlsx', 'xls'],
        accept_multiple_files=True,
        key="stock_upload"
    )
    if archivos_stock:
        st.session_state.stocks = cargar_stock(archivos_stock, st.session_state.modo)
    
    st.markdown("---")
    
    if st.session_state.carrito:
        st.markdown(f"### 🛒 Carrito")
        st.metric("Productos", len(st.session_state.carrito))
        total = sum(item.get('total', 0) for item in st.session_state.carrito)
        st.metric("Total", f"S/ {total:,.2f}")
        
        if st.button("🧹 Limpiar carrito", use_container_width=True):
            st.session_state.carrito = []
            st.rerun()

# ============================================
# TABS PRINCIPALES
# ============================================

from pages import masivo, busqueda, carrito

tab1, tab2, tab3 = st.tabs(["📦 MODO MASIVO (Bulk)", "🔍 BÚSQUEDA INTELIGENTE", "🛒 CARRITO DE COTIZACIÓN"])

with tab1:
    masivo.mostrar()

with tab2:
    busqueda.mostrar()

with tab3:
    carrito.mostrar()

# ============================================
# FOOTER
# ============================================

mostrar_footer(st.session_state.modo)
