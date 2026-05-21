# ui/tabs/skuscraper_tab.py
import streamlit as st
import pandas as pd
from collections import defaultdict


def render_skuscraper_tab():
    st.markdown("### 🔧 SKU SCRAPER - Buscador de Alternativas")
    st.caption("🔍 Encuentra SKUs alternativos con la MISMA DESCRIPCIÓN pero diferente código")
    st.caption("📌 **YESSICA / APRI.004** = Stock inmediato | **APRI.001** = Última opción (solicitar al almacén)")
    
    tiene_catalogos = st.session_state.get('catalogos', [])
    tiene_stocks = st.session_state.get('stocks', [])
    
    if not tiene_catalogos:
        st.warning("⚠️ Primero carga catálogos de precios en el sidebar")
        return
    
    if not tiene_stocks:
        st.warning("⚠️ Carga reportes de stock (YESSICA, APRI.004, APRI.001)")
        return
    
    st.markdown("---")
    
    # Buscar por descripción
    st.markdown("### 🔍 Buscar por descripción")
    st.caption("Ingresa parte de la descripción del producto que buscas")
    
    desc_buscar = st.text_input("Descripción", placeholder="Ej: Earphones Type C Black")
    
    if desc_buscar and st.button("🔍 Buscar alternativas", type="primary"):
        buscar_alternativas(desc_buscar, tiene_catalogos, tiene_stocks)


def buscar_alternativas(desc_buscar, catalogos, stocks):
    """Busca SKUs con descripción similar y muestra stock por separado"""
    desc_limpia = desc_buscar.strip().lower()
    resultados = []
    
    with st.spinner("Buscando SKUs con descripción similar..."):
        # Buscar en catálogos por descripción
        for cat in catalogos:
            df = cat['df']
            col_sku = cat['col_sku']
            col_desc = cat.get('col_desc')
            
            if not col_desc:
                continue
            
            for _, row in df.iterrows():
                desc_catalogo = str(row[col_desc]).lower()
                if desc_limpia in desc_catalogo:
                    sku = str(row[col_sku]).strip()
                    
                    # Obtener precio del nivel seleccionado
                    precio_key = st.session_state.get('precio_key', 'P. VIP')
                    precio = 0
                    if precio_key in cat.get('precios', {}):
                        col_precio = cat['precios'][precio_key]
                        try:
                            precio = float(row[col_precio]) if pd.notna(row[col_precio]) else 0
                        except:
                            precio = 0
                    
                    resultados.append({
                        'sku': sku,
                        'descripcion': str(row[col_desc])[:150],
                        'precio': precio,
                        'catalogo': cat['nombre'][:25]
                    })
    
    if not resultados:
        st.warning("No se encontraron SKUs con esa descripción")
        return
    
    # Para cada SKU, buscar su stock en las hojas
    st.success(f"✅ Se encontraron {len(resultados)} SKUs con descripción similar")
    st.markdown("---")
    
    # Mostrar resultados en cards
    for r in resultados:
        sku = r['sku']
        
        # Buscar stock en cada hoja por separado
        stock_yessica = 0
        stock_apri004 = 0
        stock_apri001 = 0
        ubicaciones = []
        
        for stock in stocks:
            df = stock['df']
            col_sku = stock['col_sku']
            hoja = stock.get('hoja', '')
            
            # Detectar columna de cantidad
            col_cant = None
            for col in df.columns:
                col_upper = str(col).upper()
                if any(p in col_upper for p in ['CANT', 'STOCK', 'DISPONIBLE', 'UNIDADES']):
                    col_cant = col
                    break
            
            if not col_cant:
                continue
            
            mask = df[col_sku].astype(str).str.strip().str.upper() == sku.upper()
            if mask.any():
                row = df[mask].iloc[0]
                cantidad = 0
                if col_cant and pd.notna(row[col_cant]):
                    try:
                        cantidad = int(float(row[col_cant]))
                    except:
                        cantidad = 0
                
                ubicaciones.append({'hoja': hoja, 'cantidad': cantidad})
                
                if 'YESSICA' in hoja.upper():
                    stock_yessica = cantidad
                elif 'APRI.004' in hoja.upper():
                    stock_apri004 = cantidad
                elif 'APRI.001' in hoja.upper():
                    stock_apri001 = cantidad
        
        # Calcular stock inmediato (YESSICA + APRI.004)
        stock_inmediato = stock_yessica + stock_apri004
        tiene_stock_inmediato = stock_inmediato > 0
        tiene_stock_remoto = stock_apri001 > 0
        
        # Determinar color y mensaje
        if tiene_stock_inmediato:
            color_borde = "#4CAF50"
            estado = "✅ STOCK INMEDIATO DISPONIBLE"
            estado_color = "#4CAF50"
        elif tiene_stock_remoto:
            color_borde = "#FF9800"
            estado = "⚠️ SOLO STOCK REMOTO (APRI.001) - Solicitar al almacén"
            estado_color = "#FF9800"
        else:
            color_borde = "#f44336"
            estado = "❌ SIN STOCK"
            estado_color = "#f44336"
        
        # Mostrar card
        st.markdown(f"""
        <div style="background:white; border-radius:16px; padding:1rem; margin-bottom:1rem; border-left:5px solid {color_borde}; box-shadow:0 2px 8px rgba(0,0,0,0.1);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                <span style="font-family:monospace; font-weight:bold; background:#e3f2fd; padding:4px 12px; border-radius:8px; color:#1565c0; font-size:0.9rem;">📦 {sku}</span>
                <span style="background:{color_borde}; color:white; padding:4px 12px; border-radius:20px; font-size:0.7rem; font-weight:bold;">{estado}</span>
            </div>
            <div style="font-size:0.85rem; color:#333; margin-bottom:0.75rem; line-height:1.4;">
                📝 {r['descripcion']}
            </div>
            <div style="display:flex; flex-wrap:wrap; gap:1rem; margin-bottom:0.75rem; padding:0.5rem; background:#f9f9f9; border-radius:10px;">
                <div style="background:#4CAF50; color:white; padding:4px 12px; border-radius:15px; font-size:0.7rem;">🟢 YESSICA: {stock_yessica}</div>
                <div style="background:#FF9800; color:white; padding:4px 12px; border-radius:15px; font-size:0.7rem;">🟡 APRI.004: {stock_apri004}</div>
                <div style="background:#f44336; color:white; padding:4px 12px; border-radius:15px; font-size:0.7rem;">🔴 APRI.001: {stock_apri001}</div>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div style="font-size:1rem;">💰 Precio <strong style="color:#e67e22;">{st.session_state.get('precio_key', 'P. VIP')}</strong>: <strong style="color:#e67e22; font-size:1.2rem;">S/ {r['precio']:.2f}</strong></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Selector de cantidad
        col1, col2 = st.columns([2, 1])
        with col1:
            if tiene_stock_inmediato:
                max_cantidad = stock_inmediato
                ayuda = f"Máximo disponible en stock inmediato: {stock_inmediato} unidades"
            elif tiene_stock_remoto:
                max_cantidad = stock_apri001
                ayuda = f"Máximo disponible en APRI.001: {stock_apri001} unidades (solicitar al almacén)"
            else:
                max_cantidad = 0
                ayuda = "No hay stock disponible"
            
            cantidad = st.number_input(
                f"Cantidad para {sku}",
                min_value=0,
                max_value=max_cantidad if max_cantidad > 0 else 1,
                value=0,
                step=1,
                key=f"cant_{sku}",
                help=ayuda,
                disabled=max_cantidad == 0
            )
        with col2:
            if cantidad > 0 and st.button(f"➕ Agregar {sku}", key=f"add_{sku}", use_container_width=True):
                item = {
                    'sku': sku,
                    'descripcion': r['descripcion'],
                    'cantidad': cantidad,
                    'precio': r['precio'],
                    'total': r['precio'] * cantidad,
                    'stock_yessica': stock_yessica,
                    'stock_apri004': stock_apri004,
                    'stock_apri001': stock_apri001,
                    'tipo_stock': 'inmediato' if tiene_stock_inmediato else 'remoto'
                }
                if 'carrito' not in st.session_state:
                    st.session_state.carrito = []
                st.session_state.carrito.append(item)
                st.success(f"✅ Agregado: {cantidad}x {sku}")
                st.rerun()
        
        st.markdown("---")
    
    # Resumen final
    if resultados:
        st.info("💡 **Tip:** Los SKUs con stock inmediato (YESSICA/APRI.004) se pueden cotizar directamente. Los de APRI.001 requieren solicitud al almacén.")


def buscar_por_sku(catalogos, stocks):
    """Busca un SKU específico y muestra su stock"""
    st.markdown("### 🔍 Búsqueda por SKU específico")
    
    sku_buscar = st.text_input("Ingresa el SKU", placeholder="Ej: RN9401276NA8")
    
    if sku_buscar and st.button("🔍 Buscar SKU", type="primary"):
        sku_limpio = sku_buscar.strip().upper()
        
        # Buscar descripción en catálogos
        descripcion = f"SKU: {sku_limpio}"
        precio = 0
        
        for cat in catalogos:
            df = cat['df']
            col_sku = cat['col_sku']
            col_desc = cat.get('col_desc')
            
            mask = df[col_sku].astype(str).str.strip().str.upper() == sku_limpio
            if mask.any():
                row = df[mask].iloc[0]
                if col_desc:
                    descripcion = str(row[col_desc])[:200]
                precio_key = st.session_state.get('precio_key', 'P. VIP')
                if precio_key in cat.get('precios', {}):
                    col_precio = cat['precios'][precio_key]
                    try:
                        precio = float(row[col_precio]) if pd.notna(row[col_precio]) else 0
                    except:
                        precio = 0
                break
        
        # Buscar stock
        stock_yessica = 0
        stock_apri004 = 0
        stock_apri001 = 0
        
        for stock in stocks:
            df = stock['df']
            col_sku = stock['col_sku']
            hoja = stock.get('hoja', '')
            
            col_cant = None
            for col in df.columns:
                col_upper = str(col).upper()
                if any(p in col_upper for p in ['CANT', 'STOCK', 'DISPONIBLE']):
                    col_cant = col
                    break
            
            if not col_cant:
                continue
            
            mask = df[col_sku].astype(str).str.strip().str.upper() == sku_limpio
            if mask.any():
                row = df[mask].iloc[0]
                cantidad = 0
                if col_cant and pd.notna(row[col_cant]):
                    try:
                        cantidad = int(float(row[col_cant]))
                    except:
                        cantidad = 0
                
                if 'YESSICA' in hoja.upper():
                    stock_yessica = cantidad
                elif 'APRI.004' in hoja.upper():
                    stock_apri004 = cantidad
                elif 'APRI.001' in hoja.upper():
                    stock_apri001 = cantidad
        
        stock_inmediato = stock_yessica + stock_apri004
        
        st.markdown(f"""
        <div style="background:white; border-radius:16px; padding:1rem; margin-top:1rem; border-left:5px solid { '#4CAF50' if stock_inmediato > 0 else '#FF9800' if stock_apri001 > 0 else '#f44336' }; box-shadow:0 2px 8px rgba(0,0,0,0.1);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                <span style="font-family:monospace; font-weight:bold; background:#e3f2fd; padding:4px 12px; border-radius:8px; color:#1565c0; font-size:0.9rem;">📦 {sku_limpio}</span>
            </div>
            <div style="font-size:0.85rem; color:#333; margin-bottom:0.75rem;">📝 {descripcion}</div>
            <div style="display:flex; flex-wrap:wrap; gap:1rem; margin-bottom:0.75rem;">
                <div style="background:#4CAF50; color:white; padding:4px 12px; border-radius:15px; font-size:0.7rem;">🟢 YESSICA: {stock_yessica}</div>
                <div style="background:#FF9800; color:white; padding:4px 12px; border-radius:15px; font-size:0.7rem;">🟡 APRI.004: {stock_apri004}</div>
                <div style="background:#f44336; color:white; padding:4px 12px; border-radius:15px; font-size:0.7rem;">🔴 APRI.001: {stock_apri001}</div>
            </div>
            <div style="font-size:1rem;">💰 Precio: <strong style="color:#e67e22;">S/ {precio:.2f}</strong></div>
        </div>
        """, unsafe_allow_html=True)
