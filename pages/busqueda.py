# pages/busqueda.py - VERSIÓN CORREGIDA (soporte UGREEN)

import streamlit as st
from modules.search_engine import (
    buscar_productos_profesional, 
    autocompletar_busqueda,
    obtener_productos_destacados
)
from modules.stock_engine import buscar_ugreen_producto  # ← IMPORTAR
from modules.ui_components import construir_badge_stock, badge_ugreen
from utils.helpers import formatear_moneda

def mostrar():
    st.markdown("### 🔍 Búsqueda Inteligente Profesional")
    st.caption("🔎 Búsqueda difusa | Tolerancia a errores | Filtros en tiempo real")
    
    # ========== VALIDACIÓN DE MODO ==========
    if st.session_state.modo == "XIAOMI":
        if not st.session_state.catalogos or not st.session_state.stocks:
            st.warning("📌 Carga catálogos y stock en el panel izquierdo")
            return
        mostrar_busqueda_xiaomi()
    
    elif st.session_state.modo == "UGREEN":
        if not st.session_state.ugreen_catalogo:
            st.warning("📌 Carga el catálogo UGREEN en el panel izquierdo")
            return
        mostrar_busqueda_ugreen()
    
    else:
        st.info("Selecciona XIAOMI o UGREEN en el panel izquierdo")

def mostrar_busqueda_xiaomi():
    """Búsqueda para XIAOMI (con fuzzy matching)"""
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        query = st.text_input("🔎 Buscar", placeholder="Ej: earphones, RN0200065BK8...", key="search_xiaomi")
    with col2:
        solo_stock = st.checkbox("📦 Solo con stock", value=True)
    with col3:
        ordenar = st.selectbox("Ordenar", ["Relevancia", "Precio ↑", "Precio ↓"])
    
    with st.expander("🔧 Filtros avanzados"):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            precio_min = st.number_input("Precio mínimo", min_value=0, value=0, step=10)
        with col_f2:
            precio_max = st.number_input("Precio máximo", min_value=0, value=100000, step=100)
    
    if query and len(query) >= 2:
        with st.spinner("🔍 Buscando..."):
            filtros = {"solo_stock": solo_stock, "precio_min": precio_min if precio_min > 0 else None, "precio_max": precio_max if precio_max < 100000 else None}
            resultados = buscar_productos_profesional(query, st.session_state.catalogos, st.session_state.stocks, st.session_state.precio_key, filtros)
            
            if not resultados:
                st.warning(f"No se encontraron resultados para '{query}'")
                return
            
            st.markdown(f"### 📊 {len(resultados)} resultados")
            
            if ordenar == "Precio ↑":
                resultados.sort(key=lambda x: x['precio'] or 999999)
            elif ordenar == "Precio ↓":
                resultados.sort(key=lambda x: x['precio'] or 0, reverse=True)
            
            for prod in resultados[:50]:
                badges = construir_badge_stock(prod['stock_yessica'], prod['stock_apri004'], prod['stock_apri001'])
                
                if prod['tiene_stock'] and prod['tiene_precio']:
                    color = "#4CAF50"
                    estado = "✅ Disponible"
                elif prod['tiene_stock'] and not prod['tiene_precio']:
                    color = "#f44336"
                    estado = "⚠️ Stock sin precio"
                elif not prod['tiene_stock'] and prod['tiene_precio']:
                    color = "#2196F3"
                    estado = "📋 Solo precio"
                else:
                    color = "#9e9e9e"
                    estado = "❌ No disponible"
                
                st.markdown(f"""
                <div style="background:white;border-radius:16px;padding:1rem;margin-bottom:1rem;border-left:5px solid {color};">
                    <div style="display:flex;justify-content:space-between;">
                        <div><strong style="color:#1a1a2e;">📦 {prod['sku']}</strong> <span style="background:{color};color:white;padding:2px 10px;border-radius:20px;">{estado}</span></div>
                        <div style="font-size:1.3rem;font-weight:bold;color:#e67e22;">{formatear_moneda(prod['precio'])}</div>
                    </div>
                    <div style="margin-top:8px;"><strong>📝 Descripción:</strong> {prod['descripcion']}</div>
                    <div>{badges}</div>
                </div>
                """, unsafe_allow_html=True)
                
                if prod['tiene_stock'] and prod['tiene_precio']:
                    col_cant, col_btn = st.columns([1, 2])
                    with col_cant:
                        cantidad = st.number_input("Cantidad", min_value=1, max_value=prod['stock_total'], value=1, key=f"busq_{prod['sku']}", label_visibility="collapsed")
                    with col_btn:
                        if st.button(f"➕ Agregar", key=f"add_{prod['sku']}"):
                            st.session_state.carrito.append({
                                'sku': prod['sku'], 'descripcion': prod['descripcion'], 'cantidad': cantidad,
                                'precio': prod['precio'], 'total': prod['precio'] * cantidad,
                                'stock_yessica': prod['stock_yessica'], 'stock_apri004': prod['stock_apri004'], 'stock_apri001': prod['stock_apri001']
                            })
                            st.success(f"✅ Agregado {cantidad}x {prod['sku']}")
                            st.rerun()
                st.divider()

def mostrar_busqueda_ugreen():
    """Búsqueda para UGREEN"""
    query = st.text_input("🔎 Buscar en UGREEN", placeholder="Ej: cable, cargador, hub...", key="search_ugreen")
    
    if query and len(query) >= 2:
        with st.spinner("🔍 Buscando en UGREEN..."):
            resultados = buscar_ugreen_producto(query, st.session_state.ugreen_catalogo)
            
            if not resultados:
                st.warning(f"No se encontraron productos para '{query}'")
                return
            
            st.markdown(f"### 📊 {len(resultados)} productos encontrados")
            
            for prod in resultados:
                precio = prod['precios'].get(st.session_state.precio_key, 0)
                badge = badge_ugreen(prod['stock']) if prod['stock'] > 0 else '<span class="badge-warning">❌ Sin stock</span>'
                
                st.markdown(f"""
                <div style="background:white;border-radius:16px;padding:1rem;margin-bottom:1rem;border-left:5px solid #00BCD4;">
                    <div><strong style="color:#1a1a2e;">📦 {prod['sku']}</strong> <span style="background:#00BCD4;color:white;padding:2px 8px;border-radius:12px;">UGREEN</span></div>
                    <div style="margin-top:8px;"><strong>📝 Descripción:</strong> {prod['descripcion']}</div>
                    <div style="margin-top:8px;">💰 Precio: <strong style="color:#e67e22;">{formatear_moneda(precio)}</strong> | 📦 Stock: <strong>{prod['stock']}</strong></div>
                    <div>{badge}</div>
                </div>
                """, unsafe_allow_html=True)
                
                if prod['tiene_stock'] and precio > 0:
                    col_cant, col_btn = st.columns([1, 2])
                    with col_cant:
                        cantidad = st.number_input("Cantidad", min_value=1, max_value=prod['stock'], value=1, key=f"ugreen_{prod['sku']}", label_visibility="collapsed")
                    with col_btn:
                        if st.button(f"➕ Agregar", key=f"add_ugreen_{prod['sku']}"):
                            st.session_state.carrito.append({
                                'sku': prod['sku'], 'descripcion': prod['descripcion'], 'cantidad': cantidad,
                                'precio': precio, 'total': precio * cantidad, 'tipo': 'UGREEN'
                            })
                            st.success(f"✅ Agregado {cantidad}x {prod['sku']}")
                            st.rerun()
                st.divider()
