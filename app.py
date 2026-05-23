# app.py - QTC Smart Sales Pro v5.0 (MODO SEGURO)

import streamlit as st
from modules.auth import inicializar_sesion, mostrar_login
from modules.ui_components import (
    aplicar_estilos_globales, restaurar_sidebar, 
    mostrar_header, mostrar_footer
)
from modules.data_loader import cargar_catalogo, cargar_stock, cargar_ugreen_catalogo

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
        ["XIAOMI", "UGREEN"],
        index=0 if st.session_state.modo == "XIAOMI" else 1
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
    
    if marca_seleccionada == "XIAOMI":
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
        
        st.markdown("**📦 Reportes de stock**")
        archivos_stock = st.file_uploader(
            "Excel",
            type=['xlsx', 'xls'],
            accept_multiple_files=True,
            key="stock_upload"
        )
        if archivos_stock:
            st.session_state.stocks = cargar_stock(archivos_stock, st.session_state.modo)
    
    elif marca_seleccionada == "UGREEN":
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
    
    st.markdown("---")
    
    if st.session_state.carrito:
        total = sum(item.get('total', 0) for item in st.session_state.carrito)
        st.metric("Total Carrito", f"S/ {total:,.2f}")
        if st.button("🧹 Limpiar carrito", use_container_width=True):
            st.session_state.carrito = []
            st.rerun()

# ============================================
# TABS PRINCIPALES - VERSIÓN SEGURA
# ============================================

tab1, tab2, tab3 = st.tabs(["📦 MODO MASIVO", "🔍 BÚSQUEDA", "🛒 CARRITO"])

# ========== TAB 1: MODO MASIVO ==========
with tab1:
    st.markdown("### 📦 Modo Masivo")
    
    if st.session_state.modo == "XIAOMI":
        if not st.session_state.catalogos or not st.session_state.stocks:
            st.warning("📌 Carga catálogos y stock en el panel izquierdo")
        else:
            from modules.stock_engine import buscar_producto
            from utils.helpers import extraer_pedidos_bulk, formatear_moneda
            from modules.ui_components import construir_badge_stock
            
            texto_bulk = st.text_area("Ingresa SKUs:", height=150, 
                                       placeholder="RN0200065BK8:5\nCN0200047BK8:10")
            
            if st.button("Procesar lista", type="primary"):
                if texto_bulk:
                    pedidos = extraer_pedidos_bulk(texto_bulk)
                    if pedidos:
                        with st.spinner("Procesando..."):
                            resultados = []
                            for pedido in pedidos:
                                prod = buscar_producto(pedido['sku'], st.session_state.catalogos, 
                                                       st.session_state.stocks, st.session_state.precio_key)
                                
                                if prod['tiene_precio'] and prod['tiene_stock']:
                                    cantidad_cotizar = min(pedido['cantidad'], prod['stock_total'])
                                    estado = "✅ OK"
                                else:
                                    cantidad_cotizar = 0
                                    estado = "❌ No disponible"
                                
                                resultados.append({
                                    **prod,
                                    'cantidad_solicitada': pedido['cantidad'],
                                    'cantidad_cotizar': cantidad_cotizar,
                                    'estado': estado
                                })
                            
                            st.session_state.resultados_bulk = resultados
                            st.success(f"✅ Procesados {len(pedidos)} productos")
                    
                    if st.session_state.resultados_bulk:
                        for prod in st.session_state.resultados_bulk[:10]:
                            badges = construir_badge_stock(prod['stock_yessica'], prod['stock_apri004'], prod['stock_apri001'])
                            st.markdown(f"""
                            <div style="background:white;border-radius:12px;padding:1rem;margin-bottom:0.5rem;">
                                <strong>📦 {prod['sku']}</strong><br>
                                📝 {prod['descripcion'][:80]}<br>
                                💰 {formatear_moneda(prod['precio'])}<br>
                                {badges}
                                <strong>Estado:</strong> {prod['estado']}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if prod['cantidad_cotizar'] > 0 and prod['tiene_precio']:
                                if st.button(f"➕ Agregar {prod['sku']}", key=f"add_{prod['sku']}"):
                                    st.session_state.carrito.append({
                                        'sku': prod['sku'],
                                        'descripcion': prod['descripcion'],
                                        'cantidad': prod['cantidad_cotizar'],
                                        'precio': prod['precio'],
                                        'total': prod['precio'] * prod['cantidad_cotizar'],
                                        'stock_yessica': prod['stock_yessica'],
                                        'stock_apri004': prod['stock_apri004'],
                                        'stock_apri001': prod['stock_apri001']
                                    })
                                    st.rerun()
                    else:
                        st.info("Procesa una lista para ver resultados")
                else:
                    st.warning("Ingresa al menos un SKU")
    
    elif st.session_state.modo == "UGREEN":
        if not st.session_state.ugreen_catalogo:
            st.warning("📌 Carga el catálogo UGREEN en el panel izquierdo")
        else:
            from modules.stock_engine import buscar_ugreen_producto
            
            texto_bulk = st.text_area("Ingresa SKUs UGREEN:", height=150, 
                                       placeholder="SKU:5\nOTROSKU:10")
            
            if st.button("Procesar lista UGREEN", type="primary"):
                if texto_bulk:
                    st.info("🟢 Procesamiento UGREEN - Función en desarrollo")
                else:
                    st.warning("Ingresa al menos un SKU")
    
    else:
        st.info("Selecciona XIAOMI o UGREEN en el panel izquierdo")

# ========== TAB 2: BÚSQUEDA ==========
with tab2:
    st.markdown("### 🔍 Búsqueda Inteligente")
    
    if st.session_state.modo == "XIAOMI":
        if not st.session_state.catalogos or not st.session_state.stocks:
            st.warning("📌 Carga catálogos y stock en el panel izquierdo")
        else:
            from modules.search_engine import buscar_productos_profesional
            from modules.ui_components import construir_badge_stock
            from utils.helpers import formatear_moneda
            
            query = st.text_input("🔎 Buscar", placeholder="Ej: earphones, RN0200065BK8...")
            
            if query and len(query) >= 2:
                with st.spinner("Buscando..."):
                    resultados = buscar_productos_profesional(
                        query, st.session_state.catalogos, st.session_state.stocks, 
                        st.session_state.precio_key, {"solo_stock": True}
                    )
                    
                    if resultados:
                        for prod in resultados[:20]:
                            badges = construir_badge_stock(prod['stock_yessica'], prod['stock_apri004'], prod['stock_apri001'])
                            st.markdown(f"""
                            <div style="background:white;border-radius:12px;padding:1rem;margin-bottom:0.5rem;">
                                <strong>📦 {prod['sku']}</strong><br>
                                📝 {prod['descripcion'][:80]}<br>
                                💰 {formatear_moneda(prod['precio'])}<br>
                                {badges}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if prod['tiene_stock'] and prod['tiene_precio']:
                                col_cant, col_btn = st.columns([1, 2])
                                with col_cant:
                                    cantidad = st.number_input("Cant", min_value=1, max_value=prod['stock_total'], value=1, key=f"busq_{prod['sku']}", label_visibility="collapsed")
                                with col_btn:
                                    if st.button(f"➕ Agregar", key=f"add_{prod['sku']}"):
                                        st.session_state.carrito.append({
                                            'sku': prod['sku'], 'descripcion': prod['descripcion'], 'cantidad': cantidad,
                                            'precio': prod['precio'], 'total': prod['precio'] * cantidad,
                                            'stock_yessica': prod['stock_yessica'], 'stock_apri004': prod['stock_apri004'], 'stock_apri001': prod['stock_apri001']
                                        })
                                        st.rerun()
                            st.divider()
    
    elif st.session_state.modo == "UGREEN":
        if not st.session_state.ugreen_catalogo:
            st.warning("📌 Carga el catálogo UGREEN en el panel izquierdo")
        else:
            from modules.stock_engine import buscar_ugreen_producto
            
            query = st.text_input("🔎 Buscar en UGREEN", placeholder="Ej: cable, cargador...")
            
            if query and len(query) >= 2:
                with st.spinner("Buscando..."):
                    resultados = buscar_ugreen_producto(query, st.session_state.ugreen_catalogo)
                    
                    if resultados:
                        for prod in resultados:
                            precio = prod['precios'].get(st.session_state.precio_key, 0)
                            st.markdown(f"""
                            <div style="background:white;border-radius:12px;padding:1rem;margin-bottom:0.5rem;border-left:5px solid #00BCD4;">
                                <strong>📦 {prod['sku']}</strong> <span style="background:#00BCD4;color:white;padding:2px 8px;border-radius:12px;">UGREEN</span><br>
                                📝 {prod['descripcion'][:80]}<br>
                                💰 {formatear_moneda(precio)} | 📦 Stock: {prod['stock']}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if prod['tiene_stock'] and precio > 0:
                                col_cant, col_btn = st.columns([1, 2])
                                with col_cant:
                                    cantidad = st.number_input("Cant", min_value=1, max_value=prod['stock'], value=1, key=f"ugreen_{prod['sku']}", label_visibility="collapsed")
                                with col_btn:
                                    if st.button(f"➕ Agregar", key=f"add_ugreen_{prod['sku']}"):
                                        st.session_state.carrito.append({
                                            'sku': prod['sku'], 'descripcion': prod['descripcion'], 'cantidad': cantidad,
                                            'precio': precio, 'total': precio * cantidad, 'tipo': 'UGREEN'
                                        })
                                        st.rerun()
                            st.divider()
    
    else:
        st.info("Selecciona XIAOMI o UGREEN en el panel izquierdo")

# ========== TAB 3: CARRITO ==========
with tab3:
    st.markdown("### 🛒 Cotización actual")
    
    if not st.session_state.carrito:
        st.info("No hay productos en el carrito")
    else:
        from modules.cart_engine import generar_excel
        from utils.helpers import formatear_moneda
        from modules.ui_components import construir_badge_stock
        
        for idx, item in enumerate(st.session_state.carrito):
            col1, col2, col3, col4, col5, col6 = st.columns([2, 4, 1, 1, 1, 0.5])
            with col1:
                st.write(f"**{item['sku']}**")
            with col2:
                st.write(item['descripcion'])
            with col3:
                nueva_cant = st.number_input("Cant", min_value=0, value=item['cantidad'], step=1, key=f"edit_{idx}", label_visibility="collapsed")
                if nueva_cant != item['cantidad']:
                    if nueva_cant == 0:
                        st.session_state.carrito.pop(idx)
                        st.rerun()
                    else:
                        item['cantidad'] = nueva_cant
                        item['total'] = item['precio'] * nueva_cant
            with col4:
                st.write(f"{formatear_moneda(item['precio'])}")
            with col5:
                st.write(f"**{formatear_moneda(item['total'])}**")
            with col6:
                if st.button("🗑️", key=f"del_{idx}"):
                    st.session_state.carrito.pop(idx)
                    st.rerun()
            
            if item.get('tipo') == 'UGREEN':
                st.markdown('<span class="badge-ugreen">📦 UGREEN</span>', unsafe_allow_html=True)
            else:
                badges = construir_badge_stock(item.get('stock_yessica', 0), item.get('stock_apri004', 0), item.get('stock_apri001', 0))
                st.markdown(badges, unsafe_allow_html=True)
            st.divider()
        
        total_general = sum(item['total'] for item in st.session_state.carrito)
        st.markdown(f"### TOTAL: {formatear_moneda(total_general)}")
        
        st.markdown("### 📋 Datos del cliente")
        cliente = st.text_input("Nombre del cliente", placeholder="Ej: Empresa SAC")
        ruc = st.text_input("RUC/DNI", placeholder="Ej: 20123456789")
        
        if st.button("📥 Exportar Excel", type="primary"):
            if cliente:
                items_export = [{'sku': i['sku'], 'descripcion': i['descripcion'], 'cantidad': i['cantidad'], 'precio': i['precio'], 'total': i['total']} for i in st.session_state.carrito]
                excel = generar_excel(items_export, cliente, ruc)
                st.download_button("💾 Descargar", data=excel, file_name=f"Cotizacion_{cliente}.xlsx")
                st.balloons()
            else:
                st.warning("Ingresa el nombre del cliente")

# ============================================
# FOOTER
# ============================================

mostrar_footer(st.session_state.modo)
