# ui/tabs/skuscraper_tab.py
import streamlit as st
import pandas as pd
from difflib import SequenceMatcher
from collections import defaultdict


def render_skuscraper_tab():
    st.markdown("### 🔧 SKU SCRAPER - Buscador de Alternativas")
    st.caption("🔍 Encuentra TODOS los SKUs con la MISMA DESCRIPCIÓN")
    st.caption("📌 Busca en: Catálogos de precios + Hojas de stock (YESSICA, APRI.004, APRI.001)")
    
    tiene_catalogos = st.session_state.get('catalogos', [])
    tiene_stocks = st.session_state.get('stocks', [])
    
    if not tiene_catalogos:
        st.warning("⚠️ Primero carga catálogos de precios en el sidebar")
        return
    
    st.markdown("---")
    
    # Configuración de búsqueda
    col1, col2 = st.columns([3, 1])
    with col1:
        desc_buscar = st.text_input("🔍 Descripción del producto", 
                                      placeholder="Ej: Type-C Earphones, Cargador 33W, Cable USB")
    with col2:
        umbral_similitud = st.slider("🎯 % Similitud", 50, 100, 65, 5)
    
    if desc_buscar and st.button("🔍 Buscar alternativas", type="primary"):
        buscar_alternativas(desc_buscar, umbral_similitud, tiene_catalogos, tiene_stocks)
    
    st.markdown("---")
    st.markdown("### 🔍 O búsqueda por SKU exacto")
    sku_buscar = st.text_input("SKU exacto", placeholder="Ej: RN9401276NA8")
    if sku_buscar and st.button("🔍 Buscar SKU", type="secondary"):
        buscar_sku_exacto(sku_buscar, tiene_catalogos, tiene_stocks)


def calcular_similitud(texto1: str, texto2: str) -> float:
    if not texto1 or not texto2:
        return 0.0
    texto1 = texto1.lower().strip()
    texto2 = texto2.lower().strip()
    if texto1 == texto2:
        return 100.0
    return SequenceMatcher(None, texto1, texto2).ratio() * 100


def buscar_alternativas(desc_buscar, umbral, catalogos, stocks):
    """Busca SKUs con descripción SIMILAR en CATÁLOGOS y STOCK"""
    desc_limpia = desc_buscar.strip().lower()
    resultados = {}  # Diccionario para evitar duplicados por SKU
    
    with st.spinner(f"Buscando con similitud ≥ {umbral}%..."):
        
        # ========== 1. BUSCAR EN CATÁLOGOS ==========
        for cat in catalogos:
            df = cat['df']
            col_sku = cat['col_sku']
            col_desc = cat.get('col_desc')
            
            if not col_desc:
                continue
            
            for _, row in df.iterrows():
                desc_catalogo = str(row[col_desc]).lower()
                similitud = calcular_similitud(desc_limpia, desc_catalogo)
                
                if similitud >= umbral:
                    sku = str(row[col_sku]).strip()
                    
                    # Obtener precio
                    precio_key = st.session_state.get('precio_key', 'P. VIP')
                    precio = 0
                    if precio_key in cat.get('precios', {}):
                        col_precio = cat['precios'][precio_key]
                        try:
                            precio = float(row[col_precio]) if pd.notna(row[col_precio]) else 0
                        except:
                            precio = 0
                    
                    if sku not in resultados:
                        resultados[sku] = {
                            'sku': sku,
                            'descripcion': str(row[col_desc])[:200],
                            'similitud': similitud,
                            'precio': precio,
                            'fuente_catalogo': cat['nombre'][:30],
                            'stock_yessica': 0,
                            'stock_apri004': 0,
                            'stock_apri001': 0
                        }
                    else:
                        # Si ya existe, actualizar precio si este es mejor
                        if resultados[sku]['precio'] == 0 and precio > 0:
                            resultados[sku]['precio'] = precio
                            resultados[sku]['fuente_catalogo'] = cat['nombre'][:30]
        
        # ========== 2. BUSCAR EN STOCK ==========
        for stock in stocks:
            df = stock['df']
            col_sku = stock['col_sku']
            hoja = stock.get('hoja', 'Desconocida')
            
            # Detectar columna de cantidad
            col_cant = None
            for col in df.columns:
                col_upper = str(col).upper()
                if any(p in col_upper for p in ['CANT', 'STOCK', 'DISPONIBLE', 'UNIDADES']):
                    col_cant = col
                    break
            
            # Detectar columna de descripción
            col_desc = None
            for col in df.columns:
                col_upper = str(col).upper()
                if any(p in col_upper for p in ['DESC', 'DESCRIPCION', 'PRODUCTO', 'ARTICULO']):
                    col_desc = col
                    break
            
            if not col_desc:
                continue
            
            for _, row in df.iterrows():
                desc_stock = str(row[col_desc]).lower()
                similitud = calcular_similitud(desc_limpia, desc_stock)
                
                if similitud >= umbral:
                    sku = str(row[col_sku]).strip()
                    
                    cantidad = 0
                    if col_cant and pd.notna(row[col_cant]):
                        try:
                            cantidad = int(float(row[col_cant]))
                        except:
                            cantidad = 0
                    
                    if sku not in resultados:
                        resultados[sku] = {
                            'sku': sku,
                            'descripcion': str(row[col_desc])[:200],
                            'similitud': similitud,
                            'precio': 0,
                            'fuente_catalogo': None,
                            'stock_yessica': 0,
                            'stock_apri004': 0,
                            'stock_apri001': 0
                        }
                    
                    # Acumular stock según la hoja
                    if 'YESSICA' in hoja.upper():
                        resultados[sku]['stock_yessica'] += cantidad
                    elif 'APRI.004' in hoja.upper():
                        resultados[sku]['stock_apri004'] += cantidad
                    elif 'APRI.001' in hoja.upper():
                        resultados[sku]['stock_apri001'] += cantidad
        
        # ========== 3. BUSCAR PRECIO PARA SKUS SIN PRECIO ==========
        for sku, data in resultados.items():
            if data['precio'] == 0:
                for cat in catalogos:
                    df = cat['df']
                    col_sku_cat = cat['col_sku']
                    precio_key = st.session_state.get('precio_key', 'P. VIP')
                    
                    mask = df[col_sku_cat].astype(str).str.strip().str.upper() == sku.upper()
                    if mask.any():
                        row = df[mask].iloc[0]
                        if precio_key in cat.get('precios', {}):
                            col_precio = cat['precios'][precio_key]
                            try:
                                precio = float(row[col_precio]) if pd.notna(row[col_precio]) else 0
                                if precio > 0:
                                    data['precio'] = precio
                                    data['fuente_catalogo'] = cat['nombre'][:30]
                                    break
                            except:
                                pass
    
    if not resultados:
        st.warning(f"❌ No se encontraron resultados para: '{desc_buscar}'")
        st.info("💡 Tips:\n- Prueba con palabras más cortas (ej: 'earphones')\n- Baja el porcentaje de similitud")
        return
    
    # Convertir a lista y ordenar
    resultados_lista = list(resultados.values())
    resultados_lista.sort(key=lambda x: x['similitud'], reverse=True)
    
    # Estadísticas
    con_precio = sum(1 for r in resultados_lista if r['precio'] > 0)
    con_stock_inmediato = sum(1 for r in resultados_lista if r['stock_yessica'] + r['stock_apri004'] > 0)
    con_stock_remoto = sum(1 for r in resultados_lista if r['stock_apri001'] > 0)
    
    st.success(f"✅ {len(resultados_lista)} SKUs encontrados")
    st.caption(f"💰 Con precio: {con_precio} | 🟢 Stock inmediato: {con_stock_inmediato} | 🔴 Stock remoto: {con_stock_remoto}")
    
    # Mostrar resumen de la búsqueda
    st.markdown(f"""
    <div style="background:#e3f2fd; border-radius:10px; padding:0.5rem 1rem; margin-bottom:1rem;">
        <span style="color:#1565c0;">🔍 Búsqueda: <strong>"{desc_buscar}"</strong> | Umbral: {umbral}% | Encontrados: {len(resultados_lista)} SKUs</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Mostrar resultados en grid de 2 columnas
    for i in range(0, len(resultados_lista), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(resultados_lista):
                r = resultados_lista[idx]
                
                stock_inmediato = r['stock_yessica'] + r['stock_apri004']
                
                if stock_inmediato > 0:
                    color = "#4CAF50"
                    estado = "✅ STOCK INMEDIATO"
                elif r['stock_apri001'] > 0:
                    color = "#FF9800"
                    estado = "⚠️ STOCK REMOTO"
                else:
                    color = "#f44336"
                    estado = "❌ SIN STOCK"
                
                with col:
                    st.markdown(f"""
                    <div style="background:#ffffff; border-radius:12px; padding:10px; margin-bottom:10px; border-left:4px solid {color}; box-shadow:0 1px 3px rgba(0,0,0,0.1);">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <b style="color:#1a1a2e; font-size:13px;">📦 {r['sku']}</b>
                            <span style="background:{color}; color:#ffffff; padding:2px 8px; border-radius:12px; font-size:10px;">{estado}</span>
                        </div>
                        <p style="color:#333333; font-size:11px; margin:6px 0 4px 0; line-height:1.3;">📝 {r['descripcion'][:80]}</p>
                        <p style="color:#888888; font-size:9px; margin:0 0 6px 0;">🎯 {r['similitud']:.0f}% coincidencia</p>
                        <div style="display:flex; flex-wrap:wrap; gap:4px; margin:6px 0;">
                            <span style="background:#4CAF50; color:#ffffff; padding:2px 6px; border-radius:10px; font-size:9px;">🟢 Y: {r['stock_yessica']}</span>
                            <span style="background:#FF9800; color:#ffffff; padding:2px 6px; border-radius:10px; font-size:9px;">🟡 A4: {r['stock_apri004']}</span>
                            <span style="background:#f44336; color:#ffffff; padding:2px 6px; border-radius:10px; font-size:9px;">🔴 A1: {r['stock_apri001']}</span>
                        </div>
                        <p style="color:#e67e22; font-size:13px; font-weight:bold; margin:6px 0 4px 0;">
                            💰 S/ {r['precio']:.2f}
                            <span style="color:#999; font-size:9px; font-weight:normal;"> ({r['fuente_catalogo'] if r['fuente_catalogo'] else 'Sin precio'})</span>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Selector de cantidad
                    max_cant = stock_inmediato if stock_inmediato > 0 else r['stock_apri001']
                    if max_cant > 0 and r['precio'] > 0:
                        col_a, col_b = st.columns([2, 1])
                        with col_a:
                            cantidad = st.number_input(
                                "Cant", 
                                min_value=0, 
                                max_value=max_cant, 
                                value=0, 
                                step=1, 
                                key=f"qty_{r['sku']}_{idx}",
                                label_visibility="collapsed"
                            )
                        with col_b:
                            if cantidad > 0:
                                if st.button(f"➕", key=f"add_{r['sku']}_{idx}"):
                                    item = {
                                        'sku': r['sku'],
                                        'descripcion': r['descripcion'],
                                        'cantidad': cantidad,
                                        'precio': r['precio'],
                                        'total': r['precio'] * cantidad,
                                        'stock_yessica': r['stock_yessica'],
                                        'stock_apri004': r['stock_apri004'],
                                        'stock_apri001': r['stock_apri001']
                                    }
                                    if 'carrito' not in st.session_state:
                                        st.session_state.carrito = []
                                    st.session_state.carrito.append(item)
                                    st.success(f"✅ {cantidad}x {r['sku']}")
                                    st.rerun()
                    elif max_cant > 0 and r['precio'] == 0:
                        st.caption("⚠️ Sin precio - No se puede cotizar")
                    else:
                        st.caption("❌ Sin stock disponible")
    
    # Botón para enviar al Bulk
    if resultados_lista:
        st.markdown("---")
        col_bulk1, col_bulk2 = st.columns(2)
        with col_bulk1:
            if st.button(f"📋 Enviar {len(resultados_lista)} SKUs al MODO MASIVO", key="bulk_send_btn", use_container_width=True):
                st.session_state.skus_para_procesar = [r['sku'] for r in resultados_lista]
                st.success(f"✅ {len(resultados_lista)} SKUs enviados")
        with col_bulk2:
            if st.button("🗑️ Limpiar resultados", key="clear_results_btn", use_container_width=True):
                st.rerun()


def buscar_sku_exacto(sku_buscar, catalogos, stocks):
    """Busca un SKU específico en catálogos y stock"""
    sku_limpio = sku_buscar.strip().upper()
    
    # Buscar descripción y precio
    descripcion = f"SKU: {sku_limpio}"
    precio = 0
    fuente_precio = None
    
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
                    fuente_precio = cat['nombre'][:30]
                except:
                    precio = 0
            break
    
    # Buscar stock
    stock_yessica = 0
    stock_apri004 = 0
    stock_apri001 = 0
    ubicaciones = []
    
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
            ubicaciones.append(f"{hoja}: {cantidad}")
    
    stock_inmediato = stock_yessica + stock_apri004
    
    if stock_inmediato == 0 and stock_apri001 == 0 and precio == 0:
        st.warning(f"❌ No se encontró el SKU: {sku_limpio}")
        return
    
    if stock_inmediato > 0:
        color = "#4CAF50"
        estado = "✅ STOCK INMEDIATO"
    elif stock_apri001 > 0:
        color = "#FF9800"
        estado = "⚠️ STOCK REMOTO (APRI.001)"
    else:
        color = "#f44336"
        estado = "❌ SIN STOCK"
    
    st.markdown(f"""
    <div style="background:#ffffff; border-radius:12px; padding:15px; margin-top:10px; border-left:4px solid {color}; box-shadow:0 2px 8px rgba(0,0,0,0.1);">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <b style="color:#1a1a2e; font-size:16px;">📦 {sku_limpio}</b>
            <span style="background:{color}; color:#ffffff; padding:4px 12px; border-radius:20px; font-size:12px;">{estado}</span>
        </div>
        <p style="color:#333333; font-size:13px; margin-bottom:12px;">📝 {descripcion}</p>
        <div style="display:flex; flex-wrap:wrap; gap:10px; margin-bottom:12px;">
            <span style="background:#4CAF50; color:#ffffff; padding:4px 12px; border-radius:15px; font-size:11px;">🟢 YESSICA: {stock_yessica}</span>
            <span style="background:#FF9800; color:#ffffff; padding:4px 12px; border-radius:15px; font-size:11px;">🟡 APRI.004: {stock_apri004}</span>
            <span style="background:#f44336; color:#ffffff; padding:4px 12px; border-radius:15px; font-size:11px;">🔴 APRI.001: {stock_apri001}</span>
        </div>
        <p style="color:#e67e22; font-size:16px; font-weight:bold;">💰 S/ {precio:.2f}</p>
        <p style="color:#666666; font-size:10px; margin-top:8px;">📍 {', '.join(ubicaciones)}</p>
        <p style="color:#999; font-size:9px; margin-top:5px;">📚 Precio desde: {fuente_precio if fuente_precio else 'No encontrado'}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Botón para enviar al Bulk
    if st.button(f"📋 Enviar SKU {sku_limpio} al MODO MASIVO", key="exact_sku_send", use_container_width=True):
        st.session_state.skus_para_procesar = [sku_limpio]
        st.success(f"✅ SKU {sku_limpio} enviado al MODO MASIVO")
