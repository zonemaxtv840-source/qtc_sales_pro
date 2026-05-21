# ui/tabs/skuscraper_tab.py
import streamlit as st
import pandas as pd
from difflib import SequenceMatcher
from collections import defaultdict


def render_skuscraper_tab():
    st.markdown("### 🔧 SKU SCRAPER - Buscador de Alternativas")
    st.caption("🔍 Encuentra TODOS los SKUs con la MISMA DESCRIPCIÓN")
    st.caption("📌 Si un SKU tiene stock pero no precio, buscará por descripción en catálogos")
    
    tiene_catalogos = st.session_state.get('catalogos', [])
    tiene_stocks = st.session_state.get('stocks', [])
    
    if not tiene_catalogos:
        st.warning("⚠️ Primero carga catálogos de precios en el sidebar")
        return
    
    st.markdown("---")
    
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
    sku_buscar = st.text_input("SKU exacto", placeholder="Ej: RN0200065BK8")
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


def extraer_color(descripcion: str) -> str:
    colores = ['BLACK', 'WHITE', 'BLUE', 'RED', 'PINK', 'GREEN', 'YELLOW', 'PURPLE', 
              'ORANGE', 'GRAY', 'GREY', 'BROWN', 'GOLD', 'SILVER', 'BEIGE']
    for color in colores:
        if color.lower() in descripcion.lower():
            return color
    return None


def buscar_por_descripcion_en_catalogos(descripcion, catalogos, precio_key):
    """Busca un producto por su descripción en todos los catálogos"""
    mejor_match = None
    mejor_similitud = 0
    mejor_precio = 0
    mejor_sku = None
    mejor_catalogo = None
    
    desc_buscar = descripcion.lower()
    color = extraer_color(desc_buscar)
    
    for cat in catalogos:
        df = cat['df']
        col_desc = cat.get('col_desc')
        if not col_desc:
            continue
        
        if precio_key not in cat.get('precios', {}):
            continue
        
        col_precio = cat['precios'][precio_key]
        
        for _, row in df.iterrows():
            desc_cat = str(row[col_desc]).lower()
            
            # Si tiene color, debe coincidir
            if color:
                if color.lower() not in desc_cat:
                    continue
            
            similitud = calcular_similitud(desc_buscar, desc_cat)
            
            if similitud >= 70 and similitud > mejor_similitud:
                try:
                    precio = float(row[col_precio]) if pd.notna(row[col_precio]) else 0
                    if precio > 0:
                        mejor_similitud = similitud
                        mejor_precio = precio
                        mejor_sku = str(row[cat['col_sku']]).strip()
                        mejor_catalogo = cat['nombre'][:30]
                except:
                    pass
    
    return {
        'precio': mejor_precio,
        'sku_match': mejor_sku,
        'similitud': mejor_similitud,
        'catalogo': mejor_catalogo
    }


def buscar_alternativas(desc_buscar, umbral, catalogos, stocks):
    """Busca SKUs con descripción SIMILAR en CATÁLOGOS y STOCK"""
    desc_limpia = desc_buscar.strip().lower()
    resultados = {}
    
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
                            'stock_apri001': 0,
                            'precio_asignado': precio > 0
                        }
        
        # ========== 2. BUSCAR EN STOCK ==========
        for stock in stocks:
            df = stock['df']
            col_sku = stock['col_sku']
            hoja = stock.get('hoja', 'Desconocida')
            
            col_cant = None
            for col in df.columns:
                col_upper = str(col).upper()
                if any(p in col_upper for p in ['CANT', 'STOCK', 'DISPONIBLE', 'UNIDADES']):
                    col_cant = col
                    break
            
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
                            'stock_apri001': 0,
                            'precio_asignado': False
                        }
                    
                    if 'YESSICA' in hoja.upper():
                        resultados[sku]['stock_yessica'] += cantidad
                    elif 'APRI.004' in hoja.upper():
                        resultados[sku]['stock_apri004'] += cantidad
                    elif 'APRI.001' in hoja.upper():
                        resultados[sku]['stock_apri001'] += cantidad
        
        # ========== 3. BUSCAR PRECIO POR DESCRIPCIÓN PARA SKUS SIN PRECIO ==========
        precio_key = st.session_state.get('precio_key', 'P. VIP')
        
        for sku, data in resultados.items():
            if data['precio'] == 0 and data['descripcion']:
                # Buscar precio por descripción
                match = buscar_por_descripcion_en_catalogos(data['descripcion'], catalogos, precio_key)
                
                if match['precio'] > 0:
                    data['precio'] = match['precio']
                    data['precio_asignado'] = True
                    data['sku_match'] = match['sku_match']
                    data['fuente_catalogo'] = match['catalogo']
                    
                    # Mostrar notificación
                    if match['sku_match'] != sku:
                        st.info(f"🔍 Precio para **{sku}** encontrado desde SKU **{match['sku_match']}** (similitud: {match['similitud']:.0f}%)")
    
    if not resultados:
        st.warning(f"❌ No se encontraron resultados para: '{desc_buscar}'")
        return
    
    resultados_lista = list(resultados.values())
    resultados_lista.sort(key=lambda x: x['similitud'], reverse=True)
    
    con_precio = sum(1 for r in resultados_lista if r['precio'] > 0)
    con_stock = sum(1 for r in resultados_lista if r['stock_yessica'] + r['stock_apri004'] + r['stock_apri001'] > 0)
    
    st.success(f"✅ {len(resultados_lista)} SKUs encontrados")
    st.caption(f"💰 Con precio: {con_precio} | 📦 Con stock: {con_stock}")
    
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
                    # Notificación de precio asignado
                    precio_nota = ""
                    if r.get('precio_asignado') and r.get('sku_match') and r['sku_match'] != r['sku']:
                        precio_nota = f'<div style="background:#FFF3E0; border-radius:8px; padding:4px; margin:6px 0; font-size:10px; color:#e67e22;">⚠️ Precio asignado desde SKU: {r["sku_match"]}</div>'
                    
                    st.markdown(f"""
                    <div style="background:#ffffff; border-radius:12px; padding:10px; margin-bottom:10px; border-left:4px solid {color}; box-shadow:0 1px 3px rgba(0,0,0,0.1);">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:5px;">
                            <b style="color:#1a1a2e; font-size:13px;">📦 {r['sku']}</b>
                            <span style="background:{color}; color:#ffffff; padding:2px 8px; border-radius:12px; font-size:10px;">{estado}</span>
                        </div>
                        <p style="color:#333333; font-size:11px; margin:5px 0;">📝 {r['descripcion'][:80]}</p>
                        <p style="color:#888888; font-size:9px; margin:0 0 5px 0;">🎯 {r['similitud']:.0f}% coincidencia</p>
                        <div style="display:flex; flex-wrap:wrap; gap:4px; margin:5px 0;">
                            <span style="background:#4CAF50; color:#ffffff; padding:2px 6px; border-radius:10px; font-size:9px;">🟢 Y: {r['stock_yessica']}</span>
                            <span style="background:#FF9800; color:#ffffff; padding:2px 6px; border-radius:10px; font-size:9px;">🟡 A4: {r['stock_apri004']}</span>
                            <span style="background:#f44336; color:#ffffff; padding:2px 6px; border-radius:10px; font-size:9px;">🔴 A1: {r['stock_apri001']}</span>
                        </div>
                        {precio_nota}
                        <p style="color:#e67e22; font-size:13px; font-weight:bold; margin:5px 0 0 0;">💰 S/ {r['precio']:.2f}</p>
                        <p style="color:#999; font-size:8px; margin:2px 0 0 0;">📚 {r['fuente_catalogo'] if r['fuente_catalogo'] else 'Precio no encontrado'}</p>
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
                                    if r.get('sku_match') and r['sku_match'] != r['sku']:
                                        st.success(f"✅ {cantidad}x {r['sku']} (precio desde {r['sku_match']})")
                                    else:
                                        st.success(f"✅ {cantidad}x {r['sku']} agregado")
                                    st.rerun()
                    elif max_cant > 0 and r['precio'] == 0:
                        st.caption("⚠️ Sin precio - No se puede cotizar")
                    else:
                        st.caption("❌ Sin stock disponible")
    
    if resultados_lista:
        st.markdown("---")
        if st.button(f"📋 Enviar {len(resultados_lista)} SKUs al MODO MASIVO", key="bulk_send_btn", use_container_width=True):
            st.session_state.skus_para_procesar = [r['sku'] for r in resultados_lista]
            st.success(f"✅ {len(resultados_lista)} SKUs enviados")


def buscar_sku_exacto(sku_buscar, catalogos, stocks):
    """Busca un SKU específico en catálogos y stock"""
    sku_limpio = sku_buscar.strip().upper()
    
    descripcion = f"SKU: {sku_limpio}"
    precio = 0
    fuente_precio = None
    precio_asignado = False
    sku_match = None
    
    # Buscar precio por SKU exacto
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
    
    # Si no se encontró precio por SKU, buscar por descripción
    if precio == 0 and descripcion and descripcion != f"SKU: {sku_limpio}":
        precio_key = st.session_state.get('precio_key', 'P. VIP')
        match = buscar_por_descripcion_en_catalogos(descripcion, catalogos, precio_key)
        if match['precio'] > 0:
            precio = match['precio']
            fuente_precio = match['catalogo']
            precio_asignado = True
            sku_match = match['sku_match']
    
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
    
    precio_nota = ""
    if precio_asignado and sku_match:
        precio_nota = f'<div style="background:#FFF3E0; border-radius:8px; padding:6px; margin-top:8px; font-size:11px; color:#e67e22;">⚠️ Precio asignado desde SKU: {sku_match}</div>'
    
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
        <p style="color:#999; font-size:9px;">📚 Precio desde: {fuente_precio if fuente_precio else 'No encontrado'}</p>
        {precio_nota}
    </div>
    """, unsafe_allow_html=True)
    
    if st.button(f"📋 Enviar SKU {sku_limpio} al MODO MASIVO", key="exact_sku_send", use_container_width=True):
        st.session_state.skus_para_procesar = [sku_limpio]
        st.success(f"✅ SKU {sku_limpio} enviado")
