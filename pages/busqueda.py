import streamlit as st
import pandas as pd
from modules.stock_engine import buscar_stock_para_sku
from modules.ui_components import construir_badge_stock
from utils.helpers import corregir_numero

def mostrar():
    st.markdown("### 🔍 Buscar productos por SKU o descripción")
    st.caption(f"🔎 Modo: **{st.session_state.modo}** | Busca por SKU o cualquier palabra")
    
    busqueda = st.text_input("", placeholder="Ej: 'RN0200065BK8' o 'Type-C Earphones'")
    
    if busqueda and len(busqueda) >= 2:
        if st.session_state.modo == "XIAOMI" and st.session_state.catalogos and st.session_state.stocks:
            buscar_xiaomi(busqueda)
        elif st.session_state.modo == "UGREEN" and st.session_state.ugreen_catalogo:
            buscar_ugreen(busqueda)

def buscar_xiaomi(busqueda):
    with st.spinner("🔍 Buscando..."):
        productos_por_sku = {}
        
        for cat in st.session_state.catalogos:
            df = cat['df']
            col_sku = cat['col_sku']
            col_desc = cat.get('col_desc')
            
            mask_sku = df[col_sku].astype(str).str.contains(busqueda, case=False, na=False)
            mask_desc = pd.Series([False] * len(df))
            if col_desc:
                mask_desc = df[col_desc].astype(str).str.contains(busqueda, case=False, na=False)
            mask = mask_sku | mask_desc
            
            for _, row in df[mask].iterrows():
                sku = str(row[col_sku]).strip().upper()
                descripcion = str(row[col_desc])[:200] if col_desc else f"SKU: {sku}"
                precio = 0.0
                if st.session_state.precio_key in cat['precios']:
                    col_precio = cat['precios'][st.session_state.precio_key]
                    precio = corregir_numero(row[col_precio])
                stock_info = buscar_stock_para_sku(sku, st.session_state.stocks)
                
                if sku in productos_por_sku:
                    existente = productos_por_sku[sku]
                    if precio > existente['precio']:
                        existente['precio'] = precio
                    if stock_info['yessica'] > 0:
                        existente['stock_yessica'] = stock_info['yessica']
                    if stock_info['apri004'] > 0:
                        existente['stock_apri004'] = stock_info['apri004']
                    if stock_info['apri001'] > 0:
                        existente['stock_apri001'] = stock_info['apri001']
                    existente['stock_total'] = existente['stock_yessica'] + existente['stock_apri004'] + existente['stock_apri001']
                    existente['tiene_stock'] = existente['stock_total'] > 0
                else:
                    productos_por_sku[sku] = {
                        'sku': sku,
                        'descripcion': descripcion,
                        'precio': precio,
                        'stock_yessica': stock_info['yessica'],
                        'stock_apri004': stock_info['apri004'],
                        'stock_apri001': stock_info['apri001'],
                        'stock_total': stock_info['total'],
                        'tiene_stock': stock_info['total'] > 0,
                        'tiene_precio': precio > 0
                    }
        
        if productos_por_sku:
            st.success(f"✅ {len(productos_por_sku)} productos encontrados")
            resultados_lista = list(productos_por_sku.values())
            resultados_lista.sort(key=lambda x: (-x['tiene_stock'], -x['tiene_precio']))
            
            for prod in resultados_lista:
                badge_stock = construir_badge_stock(prod['stock_yessica'], prod['stock_apri004'], prod['stock_apri001'])
                
                if prod['tiene_stock'] and prod['tiene_precio']:
                    color_borde = "#4CAF50"
                    estado = "✅ CON STOCK Y PRECIO"
                elif prod['tiene_stock'] and not prod['tiene_precio']:
                    color_borde = "#f44336"
                    estado = "⚠️ STOCK SIN PRECIO"
                elif not prod['tiene_stock'] and prod['tiene_precio']:
                    color_borde = "#2196F3"
                    estado = "📋 SOLO PRECIO"
                else:
                    color_borde = "#9e9e9e"
                    estado = "❌ NO DISPONIBLE"
                
                st.markdown(f"""
                <div style="background:white;border-radius:16px;padding:1rem;margin-bottom:1rem;border-left:5px solid {color_borde};box-shadow:0 2px 4px rgba(0,0,0,0.1);">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                        <div><strong style="color:#1a1a2e;">📦 SKU: {prod['sku']}</strong></div>
                        <span style="background:{color_borde};color:white;padding:2px 8px;border-radius:12px;">{estado}</span>
                    </div>
                    <div style="margin-top:8px;color:#1a1a2e;"><strong>📝 Descripción:</strong> {prod['descripcion']}</div>
                    <div style="margin-top:8px;color:#1a1a2e;"><strong>💰 Precio {st.session_state.precio_key}:</strong> <strong style="color:#e67e22;">S/ {prod['precio']:,.2f}</strong></div>
                    <div>{badge_stock}</div>
                </div>
                """, unsafe_allow_html=True)
                
                if prod['tiene_stock'] and prod['tiene_precio']:
                    col_cant, col_btn = st.columns([1, 2])
                    with col_cant:
                        cantidad = st.number_input("Cantidad", min_value=1, max_value=prod['stock_total'], value=1, step=1, key=f"search_{prod['sku']}")
                    with col_btn:
                        if st.button(f"➕ Agregar a cotización", key=f"add_search_{prod['sku']}"):
                            item = {
                                'sku': prod['sku'],
                                'descripcion': prod['descripcion'],
                                'cantidad': cantidad,
                                'precio': prod['precio'],
                                'total': prod['precio'] * cantidad,
                                'stock_yessica': prod['stock_yessica'],
                                'stock_apri004': prod['stock_apri004'],
                                'stock_apri001': prod['stock_apri001']
                            }
                            st.session_state.carrito.append(item)
                            st.success(f"✅ Agregado {cantidad}x {prod['sku']}")
                            st.rerun()
                st.divider()
        else:
            st.info("No se encontraron productos")

def buscar_ugreen(busqueda):
    from modules.stock_engine import buscar_ugreen_producto
    
    with st.spinner("🔍 Buscando en UGREEN..."):
        resultados_ugreen = buscar_ugreen_producto(busqueda, st.session_state.ugreen_catalogo)
        if resultados_ugreen:
            st.success(f"✅ {len(resultados_ugreen)} productos encontrados")
            for prod in resultados_ugreen:
                precio = prod['precios'].get(st.session_state.precio_key, 0)
                badge_stock = '<span class="badge-ugreen">📦 UGREEN: ' + str(prod['stock']) + '</span>' if prod['stock'] > 0 else '<span class="badge-warning">❌ Sin stock</span>'
                
                st.markdown(f"""
                <div style="background:white;border-radius:16px;padding:1rem;margin-bottom:1rem;border-left:5px solid #00BCD4;">
                    <div><strong style="color:#1a1a2e;">📦 SKU: {prod['sku']}</strong> <span style="background:#00BCD4;color:white;padding:2px 8px;border-radius:12px;">UGREEN</span></div>
                    <div style="margin-top:8px;color:#1a1a2e;"><strong>📝 Descripción:</strong> {prod['descripcion']}</div>
                    <div style="margin-top:8px;color:#1a1a2e;">💰 Precio: <strong style="color:#e67e22;">S/ {precio:,.2f}</strong></div>
                    <div style="margin-top:8px;">{badge_stock}</div>
                </div>
                """, unsafe_allow_html=True)
                
                if prod['tiene_stock'] and precio > 0:
                    col_cant, col_btn = st.columns([1, 2])
                    with col_cant:
                        cantidad = st.number_input("Cantidad", min_value=1, max_value=prod['stock'], value=1, step=1, key=f"ugreen_{prod['sku']}")
                    with col_btn:
                        if st.button(f"➕ Agregar a cotización", key=f"add_ugreen_{prod['sku']}"):
                            item = {
                                'sku': prod['sku'],
                                'descripcion': prod['descripcion'],
                                'cantidad': cantidad,
                                'precio': precio,
                                'total': precio * cantidad,
                                'tipo': 'UGREEN'
                            }
                            st.session_state.carrito.append(item)
                            st.success(f"✅ Agregado {cantidad}x {prod['sku']}")
                            st.rerun()
                    st.divider()
        else:
            st.info("No se encontraron productos")
