# ui/tabs/bulk_tab.py
import streamlit as st
from modules.stock_logic import buscar_stock_para_sku, calcular_cantidad_total_segura


def render_bulk_tab():
    st.markdown("### 📦 MODO MASIVO (Bulk)")
    st.caption("Ingresa productos en formato SKU:CANTIDAD")
    st.caption(f"Modo actual: {st.session_state.get('modo', 'XIAOMI')}")
    
    texto_bulk = st.text_area(
        "📝 Lista de productos",
        height=200,
        placeholder="Ejemplo:\nRN9401276NA8:100\nCN0200047BK8:50\nRN0200065BK8:25"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Procesar lista", type="primary", use_container_width=True):
            if not texto_bulk.strip():
                st.warning("Ingresa productos en formato SKU:CANTIDAD")
            elif not st.session_state.get('catalogos', []):
                st.warning("Carga catálogos de precios en el sidebar")
            elif not st.session_state.get('stocks', []):
                st.warning("Carga reportes de stock en el sidebar")
            else:
                procesar_lista_bulk(texto_bulk)
    
    with col2:
        if st.button("🗑️ Limpiar resultados", use_container_width=True):
            if 'resultados_bulk' in st.session_state:
                del st.session_state.resultados_bulk
            st.rerun()
    
    # Mostrar resultados
    if 'resultados_bulk' in st.session_state:
        mostrar_resultados()


def procesar_lista_bulk(texto_bulk):
    """Procesa lista de SKUs"""
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
                    st.warning(f"Formato incorrecto: {line}")
    
    if not pedidos:
        st.warning("No se encontraron productos válidos")
        return
    
    with st.spinner("Procesando..."):
        resultados = []
        catalogos = st.session_state.get('catalogos', [])
        stocks = st.session_state.get('stocks', [])
        precio_key = st.session_state.get('precio_key', 'P. VIP')
        
        from modules.stock_logic import buscar_stock_para_sku, calcular_cantidad_total_segura
        from utils.excel_utils import corregir_numero
        
        for p in pedidos:
            # Buscar stock
            stock_info = buscar_stock_para_sku(p['sku'], stocks)
            
            # Buscar precio en catálogos
            precio = 0
            descripcion = f"SKU: {p['sku']}"
            
            for cat in catalogos:
                df = cat['df']
                col_sku = cat['col_sku']
                col_desc = cat.get('col_desc')
                
                mask = df[col_sku].astype(str).str.strip().str.upper() == p['sku'].upper()
                if mask.any():
                    row = df[mask].iloc[0]
                    if precio_key in cat.get('precios', {}):
                        col_precio = cat['precios'][precio_key]
                        precio = corregir_numero(row[col_precio])
                    if col_desc:
                        descripcion = str(row[col_desc])[:200]
                    break
            
            # Calcular cantidad cotizable
            cantidad_cotizar, mensaje, detalle = calcular_cantidad_total_segura(
                p['cantidad'],
                {'yessica': stock_info['yessica'], 'apri004': stock_info['apri004'], 'apri001': stock_info['apri001']}
            )
            
            resultados.append({
                'sku': p['sku'],
                'descripcion': descripcion,
                'cantidad_solicitada': p['cantidad'],
                'cantidad_cotizar': cantidad_cotizar,
                'precio': precio,
                'estado': mensaje,
                'stock_yessica': stock_info['yessica'],
                'stock_apri004': stock_info['apri004'],
                'stock_apri001': stock_info['apri001'],
                'tiene_precio': precio > 0,
                'tiene_stock': stock_info['total'] > 0
            })
        
        st.session_state.resultados_bulk = resultados
        st.success(f"✅ Procesados {len(pedidos)} productos")


def mostrar_resultados():
    """Muestra resultados del procesamiento"""
    st.markdown("---")
    st.markdown("### 📋 Resultados")
    
    for r in st.session_state.resultados_bulk:
        if r['cantidad_cotizar'] > 0 and r['tiene_precio']:
            color = "#4CAF50"
            estado = "✅ COTIZABLE"
        elif r['tiene_stock'] and not r['tiene_precio']:
            color = "#FF9800"
            estado = "⚠️ STOCK SIN PRECIO"
        else:
            color = "#f44336"
            estado = "❌ NO COTIZABLE"
        
        st.markdown(f"""
        <div style="background:#ffffff; border-radius:12px; padding:10px; margin-bottom:10px; border-left:4px solid {color};">
            <div style="display:flex; justify-content:space-between;">
                <b style="color:#1a1a2e;">📦 {r['sku']}</b>
                <span style="background:{color}; color:white; padding:2px 8px; border-radius:12px;">{estado}</span>
            </div>
            <p style="color:#333; font-size:11px;">📝 {r['descripcion'][:80]}</p>
            <div style="display:flex; gap:8px; margin:5px 0;">
                <span style="background:#4CAF50; color:white; padding:2px 6px; border-radius:10px;">🟢 Y: {r['stock_yessica']}</span>
                <span style="background:#FF9800; color:white; padding:2px 6px; border-radius:10px;">🟡 A4: {r['stock_apri004']}</span>
                <span style="background:#f44336; color:white; padding:2px 6px; border-radius:10px;">🔴 A1: {r['stock_apri001']}</span>
            </div>
            <p style="color:#e67e22; font-weight:bold;">💰 S/ {r['precio']:.2f}</p>
            <p style="color:#555; font-size:10px;">📌 {r['estado']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Botón para agregar al carrito
        if r['cantidad_cotizar'] > 0 and r['tiene_precio']:
            if st.button(f"➕ Agregar {r['cantidad_cotizar']}x {r['sku']}", key=f"add_bulk_{r['sku']}"):
                item = {
                    'sku': r['sku'],
                    'descripcion': r['descripcion'],
                    'cantidad': r['cantidad_cotizar'],
                    'precio': r['precio'],
                    'total': r['precio'] * r['cantidad_cotizar'],
                    'stock_yessica': r['stock_yessica'],
                    'stock_apri004': r['stock_apri004'],
                    'stock_apri001': r['stock_apri001']
                }
                if 'carrito' not in st.session_state:
                    st.session_state.carrito = []
                st.session_state.carrito.append(item)
                st.success(f"✅ Agregado {r['cantidad_cotizar']}x {r['sku']}")
                st.rerun()
    
    if st.button("🗑️ Limpiar resultados", use_container_width=True):
        del st.session_state.resultados_bulk
        st.rerun()
