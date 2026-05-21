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
    resultados = {}  # diccionario por SKU
    
    with st.spinner(f"Buscando en CATÁLOGOS y STOCK con similitud ≥ {umbral}%..."):
        
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
                            'stock_apri001': 0,
                            'ubicaciones': []
                        }
                    else:
                        if resultados[sku]['precio'] == 0 and precio > 0:
                            resultados[sku]['precio'] = precio
        
        # ========== 2. BUSCAR EN STOCK (YESSICA, APRI.004, APRI.001) ==========
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
                    
                    # Obtener cantidad
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
                            'ubicaciones': []
                        }
                    
                    # Acumular stock según la hoja
                    if 'YESSICA' in hoja.upper():
                        resultados[sku]['stock_yessica'] += cantidad
                        resultados[sku]['ubicaciones'].append(f"YESSICA: {cantidad}")
                    elif 'APRI.004' in hoja.upper():
                        resultados[sku]['stock_apri004'] += cantidad
                        resultados[sku]['ubicaciones'].append(f"APRI.004: {cantidad}")
                    elif 'APRI.001' in hoja.upper():
                        resultados[sku]['stock_apri001'] += cantidad
                        resultados[sku]['ubicaciones'].append(f"APRI.001: {cantidad}")
                    else:
                        resultados[sku]['ubicaciones'].append(f"{hoja}: {cantidad}")
        
        # ========== 3. PARA CADA SKU, BUSCAR PRECIO EN CATÁLOGOS ==========
        for sku in list(resultados.keys()):
            if resultados[sku]['precio'] == 0:
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
                                resultados[sku]['precio'] = float(row[col_precio]) if pd.notna(row[col_precio]) else 0
                                resultados[sku]['fuente_catalogo'] = cat['nombre'][:30]
                            except:
                                pass
    
    if not resultados:
        st.warning(f"❌ No se encontraron SKUs con similitud ≥ {umbral}% para: '{desc_buscar}'")
        st.info("💡 **Tips:**\n- Prueba con palabras más cortas (ej: 'earphones')\n- Baja el porcentaje de similitud")
        return
    
    # Ordenar por similitud
    resultados_lista = list(resultados.values())
    resultados_lista.sort(key=lambda x: x['similitud'], reverse=True)
    
    st.success(f"✅ Se encontraron {len(resultados_lista)} SKUs con descripción similar")
    
    # Mostrar la búsqueda
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
                    color_borde = "#4CAF50"
                    estado = "✅ STOCK INMEDIATO"
                    estado_color = "#4CAF50"
                elif r['stock_apri001'] > 0:
                    color_borde = "#FF9800"
                    estado = "⚠️ STOCK REMOTO (APRI.001)"
                    estado_color = "#FF9800"
                else:
                    color_borde = "#f44336"
                    estado = "❌ SIN STOCK"
                    estado_color = "#f44336"
                
                with col:
                    st.markdown(f"""
                    <div style="background:white; border-radius:16px; padding:1rem; margin-bottom:1rem; border-left:5px solid {color_borde}; box-shadow:0 2px 8px rgba(0,0,0,0.1);">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                            <span style="font-family:monospace; font-weight:bold; background:#e3f2fd; padding:4px 12px; border-radius:8px; color:#1565c0; font-size:0.9rem;">📦 {r['sku']}</span>
                            <span style="background:{estado_color}; color:white; padding:4px 12px; border-radius:20px; font-size:0.7rem; font-weight:bold;">{estado}</span>
                        </div>
                        <div style="font-size:0.75rem; color:#666; margin-bottom:0.25rem;">🎯 {r['similitud']:.0f}% coincidencia</div>
                        <div style="font-size:0.8rem; color:#333; margin-bottom:0.5rem; line-height:1.3;">📝 {r['descripcion'][:100]}</div>
                        <div style="display:flex; flex-wrap:wrap; gap:0.5rem; margin-bottom:0.5rem;">
                            <div style="background:#4CAF50; color:white; padding:4px 10px; border-radius:15px; font-size:0.65rem;">🟢 YESSICA: {r['stock_yessica']}</div>
                            <div style="background:#FF9800; color:white; padding:4px 10px; border-radius:15px; font-size:0.65rem;">🟡 APRI.004: {r['stock_apri004']}</div>
                            <div style="background:#f44336; color:white; padding:4px 10px; border-radius:15px; font-size:0.65rem;">🔴 APRI.001: {r['stock_apri001']}</div>
                        </div>
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div style="font-size:0.85rem;">💰 Precio: <strong style="color:#e67e22;">S/ {r['precio']:.2f}</strong></div>
                            {f'<span style="font-size:0.6rem; color:#999;">{r["fuente_catalogo"]}</span>' if r['fuente_catalogo'] else ''}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Selector de cantidad
                    if stock_inmediato > 0 or r['stock_apri001'] > 0:
                        col_q1, col_q2 = st.columns([2, 1])
                        with col_q1:
                            max_cant = stock_inmediato if stock_inmediato > 0 else r['stock_apri001']
                            ayuda = "Stock inmediato" if stock_inmediato > 0 else "Stock remoto (APRI.001)"
                            cantidad = st.number_input(
                                f"Cantidad",
                                min_value=0,
                                max_value=max_cant,
                                value=0,
                                step=1,
                                key=f"cant_{r['sku']}",
                                help=ayuda,
                                label_visibility="collapsed"
                            )
                        with col_q2:
                            if cantidad > 0 and st.button(f"➕ Agregar", key=f"add_{r['sku']}", use_container_width=True):
                                item = {
                                    'sku': r['sku'],
                                    'descripcion': r['descripcion'],
                                    'cantidad': cantidad,
                                    'precio': r['precio'],
                                    'total': r['precio'] * cantidad,
                                    'stock_yessica': r['stock_yessica'],
                                    'stock_apri004': r['stock_apri004'],
                                    'stock_apri001': r['stock_apri001'],
                                    'ubicaciones': r['ubicaciones']
                                }
                                if 'carrito' not in st.session_state:
                                    st.session_state.carrito = []
                                st.session_state.carrito.append(item)
                                st.success(f"✅ Agregado: {cantidad}x {r['sku']}")
                                st.rerun()
    
    # Botón para enviar TODOS los SKUs al Bulk
    if resultados_lista:
        st.markdown("---")
        skus_para_bulk = [r['sku'] for r in resultados_lista]
        if st.button(f"📋 Enviar {len(skus_para_bulk)} SKUs al MODO MASIVO", use_container_width=True):
            st.session_state.skus_para_procesar = skus_para_bulk
            st.success(f"✅ {len(skus_para_bulk)} SKUs enviados al MODO MASIVO")


def buscar_sku_exacto(sku_buscar, catalogos, stocks):
    """Busca un SKU específico en catálogos y stock"""
    sku_limpio = sku_buscar.strip().upper()
    
    # Buscar descripción y precio
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
    
    color_borde = "#4CAF50" if stock_inmediato > 0 else "#FF9800" if stock_apri001 > 0 else "#f44336"
    
    st.markdown(f"""
    <div style="background:white; border-radius:16px; padding:1rem; margin-top:1rem; border-left:5px solid {color_borde}; box-shadow:0 2px 8px rgba(0,0,0,0.1);">
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
        <div style="font-size:0.7rem; color:#666; margin-top:0.5rem;">📍 {', '.join(ubicaciones)}</div>
    </div>
    """, unsafe_allow_html=True)
