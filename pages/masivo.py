# pages/masivo.py
# TAB 1: MODO MASIVO

import streamlit as st
from modules.stock_engine import buscar_producto, buscar_ugreen_producto
from modules.ui_components import construir_badge_stock, badge_ugreen
from utils.helpers import extraer_pedidos_bulk, formatear_moneda

def mostrar():
    st.markdown("### 📦 Ingresa productos en formato masivo")
    st.caption(f"🔍 Modo: **{st.session_state.modo}** | Formato: `SKU:CANTIDAD` (uno por línea)")
    
    texto_bulk = st.text_area(
        "",
        height=200,
        placeholder="Ejemplo:\nRN9401276NA8:100\nCN0200047BK8:50\nRN0200065BK8:25"
    )
    
    col_b1, col_b2 = st.columns([1, 1])
    
    with col_b1:
        if st.button("🚀 Procesar lista", type="primary", use_container_width=True):
            if not texto_bulk:
                st.warning("Ingresa productos")
            elif st.session_state.modo == "XIAOMI" and not st.session_state.catalogos:
                st.warning("Carga catálogos primero")
            elif st.session_state.modo == "XIAOMI" and not st.session_state.stocks:
                st.warning("Carga stock primero")
            else:
                if st.session_state.modo == "XIAOMI":
                    procesar_xiaomi(texto_bulk)
                elif st.session_state.modo == "UGREEN":
                    procesar_ugreen(texto_bulk)
    
    with col_b2:
        if st.button("📋 Agregar válidos al carrito", use_container_width=True):
            if st.session_state.resultados_bulk:
                agregados = 0
                for prod in st.session_state.resultados_bulk:
                    if prod.get('cantidad_cotizar', 0) > 0 and prod.get('tiene_precio', False):
                        item_carrito = {
                            'sku': prod['sku'],
                            'descripcion': prod['descripcion'],
                            'cantidad': prod['cantidad_cotizar'],
                            'precio': prod['precio'],
                            'total': prod['precio'] * prod['cantidad_cotizar'],
                            'stock_yessica': prod.get('stock_yessica', 0),
                            'stock_apri004': prod.get('stock_apri004', 0),
                            'stock_apri001': prod.get('stock_apri001', 0),
                            'tipo': prod.get('tipo', 'XIAOMI')
                        }
                        st.session_state.carrito.append(item_carrito)
                        agregados += 1
                st.success(f"✅ Agregados {agregados} productos al carrito")
                st.rerun()
            else:
                st.warning("Primero procesa una lista")
    
    mostrar_resultados()

def procesar_xiaomi(texto_bulk):
    pedidos = extraer_pedidos_bulk(texto_bulk)
    
    if not pedidos:
        st.warning("No se encontraron productos válidos")
        return
    
    with st.spinner("Procesando..."):
        resultados = []
        encontrados = 0
        con_precio = 0
        con_stock = 0
        
        for pedido in pedidos:
            prod = buscar_producto(
                pedido['sku'], 
                st.session_state.catalogos, 
                st.session_state.stocks, 
                st.session_state.precio_key
            )
            
            if prod['tiene_precio']:
                encontrados += 1
                con_precio += 1
            if prod['tiene_stock']:
                con_stock += 1
            
            if prod['tiene_precio'] and prod['tiene_stock']:
                cantidad_cotizar = min(pedido['cantidad'], prod['stock_total'])
                estado = "✅ OK"
                if cantidad_cotizar < pedido['cantidad']:
                    estado = f"⚠️ Stock insuficiente ({cantidad_cotizar}/{pedido['cantidad']})"
            elif prod['tiene_stock'] and not prod['tiene_precio']:
                cantidad_cotizar = 0
                estado = "⚠️ Stock sin precio - Verificar SKU"
            elif not prod['tiene_stock'] and prod['tiene_precio']:
                cantidad_cotizar = 0
                estado = "📋 Solo precio, sin stock"
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
        
        st.markdown(f"""
        <div class="counter-summary">
            <div class="counter-item">📋 Ingresados: <strong>{len(pedidos)}</strong></div>
            <div class="counter-item" style="background:#4CAF50;color:white;">✅ Con precio: <strong>{encontrados}</strong></div>
            <div class="counter-item">📦 Con stock: <strong>{con_stock}</strong></div>
            <div class="counter-item" style="color:#f44336;">❌ Sin precio: <strong>{len(pedidos) - encontrados}</strong></div>
        </div>
        """, unsafe_allow_html=True)
        
        st.success(f"✅ Procesados {len(pedidos)} productos")

def procesar_ugreen(texto_bulk):
    pedidos = extraer_pedidos_bulk(texto_bulk)
    
    if not pedidos:
        st.warning("No se encontraron productos válidos")
        return
    
    with st.spinner("Procesando UGREEN..."):
        resultados = []
        for pedido in pedidos:
            resultados_ugreen = buscar_ugreen_producto(pedido['sku'], st.session_state.ugreen_catalogo)
            if resultados_ugreen and len(resultados_ugreen) > 0:
                prod = resultados_ugreen[0]
                precio = prod['precios'].get(st.session_state.precio_key, 0)
                if precio > 0 and prod['tiene_stock']:
                    cantidad_cotizar = min(pedido['cantidad'], prod['stock'])
                    estado = "✅ OK"
                elif precio > 0 and not prod['tiene_stock']:
                    cantidad_cotizar = 0
                    estado = "❌ Sin stock"
                else:
                    cantidad_cotizar = 0
                    estado = "❌ Sin precio"
                
                resultados.append({
                    'sku': prod['sku'],
                    'descripcion': prod['descripcion'],
                    'precio': precio,
                    'stock_total': prod['stock'],
                    'tiene_stock': prod['tiene_stock'],
                    'tiene_precio': precio > 0,
                    'cantidad_solicitada': pedido['cantidad'],
                    'cantidad_cotizar': cantidad_cotizar,
                    'estado': estado,
                    'tipo': 'UGREEN'
                })
            else:
                resultados.append({
                    'sku': pedido['sku'],
                    'descripcion': f"SKU: {pedido['sku']}",
                    'precio': 0,
                    'stock_total': 0,
                    'tiene_stock': False,
                    'tiene_precio': False,
                    'cantidad_solicitada': pedido['cantidad'],
                    'cantidad_cotizar': 0,
                    'estado': "❌ No encontrado",
                    'tipo': 'UGREEN'
                })
        
        st.session_state.resultados_bulk = resultados
        st.success(f"✅ Procesados {len(pedidos)} productos UGREEN")

def mostrar_resultados():
    if not st.session_state.resultados_bulk:
        return
    
    st.markdown("---")
    st.markdown("### 📋 Productos procesados")
    
    for prod in st.session_state.resultados_bulk:
        if prod.get('tipo') == 'UGREEN':
            badge = badge_ugreen(prod['stock_total']) if prod['stock_total'] > 0 else '<span class="badge-warning">❌ Sin stock</span>'
            st.markdown(f"""
            <div style="background:white;border-radius:16px;padding:1rem;margin-bottom:1rem;border-left:5px solid #00BCD4;">
                <div><strong style="color:#1a1a2e;">📦 SKU: {prod['sku']}</strong> <span style="background:#00BCD4;color:white;padding:2px 8px;border-radius:12px;">UGREEN</span></div>
                <div style="margin-top:8px;color:#1a1a2e;"><strong>📝 Descripción:</strong> {prod['descripcion'][:100]}</div>
                <div style="margin-top:8px;">💰 Precio: <strong style="color:#e67e22;">{formatear_moneda(prod['precio'])}</strong> | 📦 Stock: <strong>{prod['stock_total']}</strong></div>
                <div>{badge}</div>
                <div><strong>📌 Estado:</strong> {prod['estado']}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            badges = construir_badge_stock(prod['stock_yessica'], prod['stock_apri004'], prod['stock_apri001'])
            
            if prod['tiene_stock'] and prod['tiene_precio']:
                st.markdown(f"""
                <div style="background:white;border-radius:16px;padding:1rem;margin-bottom:1rem;border-left:5px solid #4CAF50;">
                    <div><strong style="color:#1a1a2e;">📦 SKU: {prod['sku']}</strong> <span style="background:#4CAF50;color:white;padding:2px 8px;border-radius:12px;">✅ CON STOCK Y PRECIO</span></div>
                    <div style="margin-top:8px;"><strong>📝 Descripción:</strong> {prod['descripcion']}</div>
                    <div>💰 Precio: <strong style="color:#e67e22;">{formatear_moneda(prod['precio'])}</strong></div>
                    <div>{badges}</div>
                    <div><strong>📌 Estado:</strong> {prod['estado']}</div>
                </div>
                """, unsafe_allow_html=True)
            elif prod['tiene_stock'] and not prod['tiene_precio']:
                st.markdown(f"""
                <div style="background:white;border-radius:16px;padding:1rem;margin-bottom:1rem;border-left:5px solid #f44336;">
                    <div><strong style="color:#1a1a2e;">📦 SKU: {prod['sku']}</strong> <span style="background:#f44336;color:white;padding:2px 8px;border-radius:12px;">⚠️ ERROR DE SKU</span></div>
                    <div style="margin-top:8px;"><strong>📝 Descripción:</strong> {prod['descripcion']}</div>
                    <div><strong>📦 Stock disponible:</strong></div>
                    <div>{badges}</div>
                </div>
                """, unsafe_allow_html=True)
                
                if prod.get('sku_equivalente'):
                    st.markdown(f"""
                    <div style="background:#E8F5E9;border-radius:12px;padding:1rem;margin:0.5rem 0;">
                        <strong style="color:#2E7D32;">💡 SKU EQUIVALENTE SUGERIDO</strong><br>
                        <strong>SKU:</strong> <code>{prod['sku_equivalente']}</code><br>
                        <strong>Precio:</strong> {formatear_moneda(prod.get('precio_equivalente', 0))}<br>
                        <strong>Coincidencia:</strong> {prod.get('similitud_equivalente', 0):.0f}%
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background:white;border-radius:16px;padding:1rem;margin-bottom:1rem;border-left:5px solid #9e9e9e;">
                    <div><strong style="color:#1a1a2e;">📦 SKU: {prod['sku']}</strong> <span style="background:#9e9e9e;color:white;padding:2px 8px;border-radius:12px;">❌ NO DISPONIBLE</span></div>
                    <div style="margin-top:8px;"><strong>📝 Descripción:</strong> {prod['descripcion']}</div>
                    <div>{badges}</div>
                </div>
                """, unsafe_allow_html=True)
    
    st.divider()
    if st.button("🗑️ Limpiar resultados", key="clear_bulk_results", use_container_width=True):
        del st.session_state.resultados_bulk
        st.rerun()
