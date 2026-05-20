# ui/tabs/bulk_tab.py - Primeras líneas
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from modules.stock_logic import buscar_stock_para_sku, calcular_cantidad_total_segura, calcular_cantidad_apri001_only
from modules.xiaomi_handler import buscar_producto
from modules.ugreen_handler import buscar_ugreen_producto
from utils.formatters import construir_badge_stock, formatear_precio
from ui.components import mostrar_resumen_bulk
def render_bulk_tab():
    modo = st.session_state.get('modo', 'XIAOMI')
    st.markdown("### 📦 Ingresa productos en formato masivo")
    st.caption(f"🔍 Modo: **{modo}** | Formato: `SKU:CANTIDAD` (uno por línea)")
    st.caption("🔒 **Reglas de stock:** YESSICA/APRI.004 = stock - 2 | APRI.001 = 15% del stock (máx 100, min 20)")
    
    texto_bulk = st.text_area(
        "",
        height=200,
        placeholder="Ejemplo:\nRN9401276NA8:100\nCN0200047BK8:100\nRN0200065BK8:50\nCN9406882NA8:25"
    )
    
    col_b1, col_b2 = st.columns([1, 1])
    
    with col_b1:
        if st.button("🚀 Procesar lista", type="primary", use_container_width=True):
            if not texto_bulk:
                st.warning("Ingresa productos en el formato correcto")
            elif modo == "XIAOMI" and not st.session_state.get('catalogos', []):
                st.warning("Carga catálogos de XIAOMI primero")
            elif modo == "XIAOMI" and not st.session_state.get('stocks', []):
                st.warning("Carga reportes de stock primero")
            elif modo == "UGREEN" and not st.session_state.get('ugreen_catalogo'):
                st.warning("Carga el catálogo de UGREEN primero")
            else:
                # Procesar según modo
                if modo == "XIAOMI":
                    procesar_bulk_xiaomi(texto_bulk)
                elif modo == "UGREEN":
                    procesar_bulk_ugreen(texto_bulk)
                else:
                    st.info("Modo OTRAS MARCAS - Próximamente")
    
    with col_b2:
        if st.button("📋 Agregar válidos al carrito", use_container_width=True):
            if hasattr(st.session_state, 'resultados_bulk') and st.session_state.resultados_bulk:
                agregar_validos_al_carrito()
            else:
                st.warning("Primero procesa una lista de productos")
    
    # Mostrar resultados si existen
    if hasattr(st.session_state, 'resultados_bulk') and st.session_state.resultados_bulk:
        mostrar_resultados_bulk()


def procesar_bulk_xiaomi(texto_bulk):
    """Procesa lista de productos en modo XIAOMI"""
    pedidos = []
    for line in texto_bulk.strip().split('\n'):
        line = line.strip()
        if ':' in line:
            parts = line.split(':')
            if len(parts) == 2:
                try:
                    sku = parts[0].strip().upper()
                    cant = int(parts[1].strip())
                    if cant > 0:
                        pedidos.append({'sku': sku, 'cantidad': cant})
                except:
                    pass
    
    if not pedidos:
        st.warning("No se encontraron productos válidos")
        return
    
    with st.spinner("Procesando XIAOMI con nueva lógica de stock..."):
        resultados_procesados = []
        encontrados = 0
        con_precio = 0
        con_stock = 0
        
        for pedido in pedidos:
            prod = buscar_producto(
                pedido['sku'], 
                st.session_state.get('catalogos', []), 
                st.session_state.get('stocks', []), 
                st.session_state.get('precio_key', 'P. VIP')
            )
            
            if prod.get('tiene_precio', False):
                encontrados += 1
                con_precio += 1
            
            if prod.get('tiene_stock', False):
                con_stock += 1
            
            # Aplicar lógica de stock
            if prod.get('tiene_precio', False) and prod.get('tiene_stock', False):
                if prod.get('usa_apri001_only', False):
                    cantidad_final, mensaje, _ = calcular_cantidad_apri001_only(
                        pedido['cantidad'], 
                        prod.get('stock_apri001', 0)
                    )
                    cantidad_cotizar = cantidad_final
                    estado = mensaje
                else:
                    cantidad_final, mensaje, _ = calcular_cantidad_total_segura(
                        pedido['cantidad'],
                        {
                            'yessica': prod.get('stock_yessica', 0),
                            'apri004': prod.get('stock_apri004', 0),
                            'apri001': prod.get('stock_apri001', 0)
                        }
                    )
                    cantidad_cotizar = cantidad_final
                    estado = mensaje
            elif not prod.get('tiene_precio', False) and prod.get('tiene_stock', False):
                cantidad_cotizar = 0
                estado = "⚠️ Stock disponible - SIN PRECIO"
            elif not prod.get('tiene_precio', False):
                cantidad_cotizar = 0
                estado = "❌ Sin precio"
            else:
                cantidad_cotizar = 0
                estado = "❌ Sin stock"
            
            resultados_procesados.append({
                **prod,
                'cantidad_solicitada': pedido['cantidad'],
                'cantidad_cotizar': cantidad_cotizar,
                'estado': estado
            })
        
        st.session_state.resultados_bulk = resultados_procesados
        mostrar_resumen_bulk(resultados_procesados)
        st.success(f"✅ Procesados {len(pedidos)} productos en modo XIAOMI")


def procesar_bulk_ugreen(texto_bulk):
    """Procesa lista de productos en modo UGREEN"""
    pedidos = []
    for line in texto_bulk.strip().split('\n'):
        line = line.strip()
        if ':' in line:
            parts = line.split(':')
            if len(parts) == 2:
                try:
                    sku = parts[0].strip().upper()
                    cant = int(parts[1].strip())
                    if cant > 0:
                        pedidos.append({'sku': sku, 'cantidad': cant})
                except:
                    pass
    
    if not pedidos:
        st.warning("No se encontraron productos válidos")
        return
    
    with st.spinner("Procesando UGREEN..."):
        resultados_procesados = []
        
        for pedido in pedidos:
            resultados_ugreen = buscar_ugreen_producto(
                pedido['sku'], 
                st.session_state.get('ugreen_catalogo')
            )
            
            if resultados_ugreen and len(resultados_ugreen) > 0:
                prod = resultados_ugreen[0]
                precio = prod['precios'].get(st.session_state.get('precio_key', 'P. VIP'), 0)
                
                if precio > 0 and prod.get('tiene_stock', False):
                    stock_seguro = max(0, prod['stock'] - 2)
                    if pedido['cantidad'] <= stock_seguro:
                        cantidad_cotizar = pedido['cantidad']
                        estado = f"✅ OK - Stock UGREEN: {prod['stock']} (seguro: {stock_seguro})"
                    elif stock_seguro > 0:
                        cantidad_cotizar = stock_seguro
                        estado = f"⚠️ Stock insuficiente. Ajustado a {stock_seguro} unidades"
                    else:
                        cantidad_cotizar = 0
                        estado = "❌ Stock muy bajo"
                elif precio > 0 and not prod.get('tiene_stock', False):
                    cantidad_cotizar = 0
                    estado = "❌ Sin stock"
                else:
                    cantidad_cotizar = 0
                    estado = "❌ Sin precio"
                
                resultados_procesados.append({
                    'sku': prod['sku'],
                    'descripcion': prod['descripcion'],
                    'precio': precio,
                    'stock_total': prod.get('stock', 0),
                    'tiene_stock': prod.get('tiene_stock', False),
                    'tiene_precio': precio > 0,
                    'cantidad_solicitada': pedido['cantidad'],
                    'cantidad_cotizar': cantidad_cotizar,
                    'estado': estado,
                    'tipo': 'UGREEN'
                })
            else:
                resultados_procesados.append({
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
        
        st.session_state.resultados_bulk = resultados_procesados
        mostrar_resumen_bulk(resultados_procesados)
        st.success(f"✅ Procesados {len(pedidos)} productos en modo UGREEN")


def agregar_validos_al_carrito():
    """Agrega productos válidos al carrito"""
    agregados = 0
    for prod in st.session_state.resultados_bulk:
        if prod.get('cantidad_cotizar', 0) > 0 and prod.get('tiene_precio', False):
            item_carrito = {
                'sku': prod['sku'],
                'descripcion': prod.get('descripcion', ''),
                'cantidad': prod['cantidad_cotizar'],
                'precio': prod.get('precio', 0),
                'total': prod.get('precio', 0) * prod.get('cantidad_cotizar', 0),
                'stock_yessica': prod.get('stock_yessica', 0),
                'stock_apri004': prod.get('stock_apri004', 0),
                'stock_apri001': prod.get('stock_apri001', 0),
                'detalle_apri001': prod.get('detalle_apri001', []),
                'ubicaciones': prod.get('ubicaciones', []),
                'tipo': prod.get('tipo', 'XIAOMI')
            }
            st.session_state.carrito.append(item_carrito)
            agregados += 1
    st.success(f"✅ Agregados {agregados} productos al carrito")
    st.rerun()


def mostrar_resultados_bulk():
    """Muestra los resultados del procesamiento bulk"""
    st.markdown("---")
    st.markdown("### 📋 Productos procesados")
    
    for prod in st.session_state.resultados_bulk:
        if prod.get('tipo') == 'UGREEN':
            badge_stock = f'<span class="badge-ugreen">📦 UGREEN: {prod.get("stock_total", 0)}</span>'
            st.markdown(f"""
            <div style="background:white;border-radius:16px;padding:1rem;margin-bottom:1rem;border-left:5px solid #00BCD4;color:#1a1a2e;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div><strong style="color:#1a1a2e;">📦 {prod['sku']}</strong> <span style="background:#00BCD4;color:white;padding:2px 8px;border-radius:12px;font-size:0.7rem;">UGREEN</span></div>
                    <div><span style="background:#2196F3;color:white;padding:2px 8px;border-radius:12px;font-size:0.7rem;">Solicitado: {prod['cantidad_solicitada']}</span></div>
                </div>
                <div style="margin-top:8px;"><span style="font-size:0.85rem;color:#1a1a2e;">{prod.get('descripcion', '')[:100]}</span></div>
                <div style="margin-top:8px;color:#1a1a2e;">💰 Precio: <strong>{formatear_precio(prod.get('precio', 0))}</strong> | Cotizable: {prod.get('cantidad_cotizar', 0)}</div>
                <div style="margin-top:8px;">{badge_stock}</div>
                <div style="margin-top:8px;color:#1a1a2e;"><strong>📌 Estado:</strong> {prod.get('estado', '')}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            badge_stock = construir_badge_stock(
                prod.get('stock_yessica', 0),
                prod.get('stock_apri004', 0),
                prod.get('stock_apri001', 0),
                prod.get('detalle_apri001', []),
                prod.get('ubicaciones', [])
            )
            
            st.markdown(f"""
            <div style="background:white;border-radius:16px;padding:1rem;margin-bottom:1rem;border-left:5px solid #4CAF50;color:#1a1a2e;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div><strong style="color:#1a1a2e;">📦 {prod['sku']}</strong></div>
                    <div><span style="background:#2196F3;color:white;padding:2px 8px;border-radius:12px;font-size:0.7rem;">Cotizar: {prod.get('cantidad_cotizar', 0)}/{prod.get('cantidad_solicitada', 0)}</span></div>
                </div>
                <div style="margin-top:8px;"><span style="font-size:0.85rem;color:#1a1a2e;">{prod.get('descripcion', '')[:100]}</span></div>
                <div style="margin-top:8px;color:#1a1a2e;">💰 Precio: <strong>{formatear_precio(prod.get('precio', 0))}</strong></div>
                <div style="margin-top:8px;">{badge_stock}</div>
                <div style="margin-top:8px;color:#1a1a2e;"><strong>📌 Estado:</strong> {prod.get('estado', '')}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
    
    if st.button("🗑️ Limpiar resultados", key="clear_bulk_results", use_container_width=True):
        del st.session_state.resultados_bulk
        st.rerun()
