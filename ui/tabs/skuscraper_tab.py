# ui/tabs/skuscraper_tab.py
import streamlit as st
import pandas as pd
from difflib import SequenceMatcher
from collections import defaultdict


# ==========================================
# CONFIGURACIÓN DE SEGURIDAD PARA PRECIOS
# ==========================================
PRICE_LIMITS = {
    "EARPHONE": 80,
    "CABLE": 50,
    "CHARGER": 150,
    "SPEAKER": 300,
    "WATCH": 400,
    "DEFAULT": 500
}


def get_product_family(description):
    desc_lower = description.lower()
    if any(word in desc_lower for word in ['earphone', 'headphone', 'audifono', 'earbud', 'airbud']):
        return "EARPHONE"
    if any(word in desc_lower for word in ['cable', 'usb', 'lightning', 'type-c']):
        return "CABLE"
    if any(word in desc_lower for word in ['charger', 'cargador', 'power adapter']):
        return "CHARGER"
    if any(word in desc_lower for word in ['speaker', 'parlante', 'sound', 'audio']):
        return "SPEAKER"
    if any(word in desc_lower for word in ['watch', 'band', 'reloj']):
        return "WATCH"
    return "DEFAULT"


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
              'ORANGE', 'GRAY', 'GREY', 'BROWN', 'GOLD', 'SILVER']
    for color in colores:
        if color.lower() in descripcion.lower():
            return color
    return None


def buscar_por_descripcion_en_catalogos(descripcion, catalogos, precio_key):
    """Busca precio por descripción con FILTROS DE SEGURIDAD"""
    desc_buscar = descripcion.lower()
    familia_origen = get_product_family(desc_buscar)
    limite_precio = PRICE_LIMITS.get(familia_origen, PRICE_LIMITS["DEFAULT"])
    color = extraer_color(desc_buscar)
    
    mejores_matches = []
    
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
            
            similitud = calcular_similitud(desc_buscar, desc_cat)
            if similitud < 75:
                continue
            
            if color:
                if color.lower() not in desc_cat:
                    continue
            
            familia_match = get_product_family(desc_cat)
            if familia_match != familia_origen:
                continue
            
            try:
                precio = float(row[col_precio]) if pd.notna(row[col_precio]) else 0
                if precio > 0 and precio <= limite_precio:
                    mejores_matches.append({
                        'precio': precio,
                        'sku_match': str(row[cat['col_sku']]).strip(),
                        'similitud': similitud,
                        'catalogo': cat['nombre'][:30]
                    })
            except:
                pass
    
    if mejores_matches:
        mejores_matches.sort(key=lambda x: x['similitud'], reverse=True)
        return mejores_matches[0]
    
    return {'precio': 0, 'sku_match': None, 'similitud': 0, 'catalogo': None}


def render_skuscraper_tab():
    st.markdown("### 🔧 SKU SCRAPER - Buscador de Alternativas")
    st.caption("🔍 Encuentra TODOS los SKUs con la MISMA DESCRIPCIÓN")
    st.caption("⚠️ **Seguridad activada**: Asigna precio automático si la descripción coincide en ≥75%")
    st.caption("✏️ **Si no hay precio automático, puedes ingresarlo manualmente**")
    
    tiene_catalogos = st.session_state.get('catalogos', [])
    tiene_stocks = st.session_state.get('stocks', [])
    
    if not tiene_catalogos:
        st.warning("⚠️ Primero carga catálogos de precios en el sidebar")
        return
    
    st.markdown("---")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        desc_buscar = st.text_input("🔍 Descripción del producto", placeholder="Ej: Type-C Earphones, Cargador 33W")
    with col2:
        umbral_similitud = st.slider("🎯 % Similitud", 50, 100, 70, 5)
    
    if desc_buscar and st.button("🔍 Buscar alternativas", type="primary"):
        buscar_alternativas(desc_buscar, umbral_similitud, tiene_catalogos, tiene_stocks)
    
    st.markdown("---")
    st.markdown("### 🔍 Búsqueda por SKU exacto (con precio manual)")
    sku_buscar = st.text_input("SKU exacto", placeholder="Ej: RN0200065BK8")
    if sku_buscar and st.button("🔍 Buscar SKU", type="secondary"):
        buscar_sku_exacto(sku_buscar, tiene_catalogos, tiene_stocks)


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
            if not col_desc: continue
            
            for _, row in df.iterrows():
                desc_catalogo = str(row[col_desc]).lower()
                similitud = calcular_similitud(desc_limpia, desc_catalogo)
                if similitud >= umbral:
                    sku = str(row[col_sku]).strip()
                    precio_key = st.session_state.get('precio_key', 'P. VIP')
                    precio = 0
                    if precio_key in cat.get('precios', {}):
                        col_precio = cat['precios'][precio_key]
                        try: precio = float(row[col_precio]) if pd.notna(row[col_precio]) else 0
                        except: pass
                    
                    if sku not in resultados:
                        resultados[sku] = {
                            'sku': sku, 'descripcion': str(row[col_desc])[:200],
                            'similitud': similitud, 'precio': precio,
                            'fuente_catalogo': cat['nombre'][:30],
                            'stock_yessica': 0, 'stock_apri004': 0, 'stock_apri001': 0,
                            'precio_asignado': precio > 0
                        }
        
        # ========== 2. BUSCAR EN STOCK ==========
        for stock in stocks:
            df = stock['df']; col_sku = stock['col_sku']; hoja = stock.get('hoja', '')
            col_cant = None
            for col in df.columns:
                if any(p in str(col).upper() for p in ['CANT', 'STOCK', 'DISPONIBLE']):
                    col_cant = col; break
            col_desc = None
            for col in df.columns:
                if any(p in str(col).upper() for p in ['DESC', 'DESCRIPCION', 'ARTICULO']):
                    col_desc = col; break
            if not col_desc: continue
            
            for _, row in df.iterrows():
                desc_stock = str(row[col_desc]).lower()
                similitud = calcular_similitud(desc_limpia, desc_stock)
                if similitud >= umbral:
                    sku = str(row[col_sku]).strip()
                    cantidad = int(row[col_cant]) if col_cant and pd.notna(row[col_cant]) else 0
                    if sku not in resultados:
                        resultados[sku] = {
                            'sku': sku, 'descripcion': str(row[col_desc])[:200],
                            'similitud': similitud, 'precio': 0, 'fuente_catalogo': None,
                            'stock_yessica': 0, 'stock_apri004': 0, 'stock_apri001': 0,
                            'precio_asignado': False
                        }
                    if 'YESSICA' in hoja.upper(): resultados[sku]['stock_yessica'] += cantidad
                    elif 'APRI.004' in hoja.upper(): resultados[sku]['stock_apri004'] += cantidad
                    elif 'APRI.001' in hoja.upper(): resultados[sku]['stock_apri001'] += cantidad
        
        # ========== 3. BUSCAR PRECIO POR DESCRIPCIÓN ==========
        precio_key = st.session_state.get('precio_key', 'P. VIP')
        for sku, data in resultados.items():
            if data['precio'] == 0 and data['descripcion']:
                match = buscar_por_descripcion_en_catalogos(data['descripcion'], catalogos, precio_key)
                if match['precio'] > 0:
                    data['precio'] = match['precio']
                    data['precio_asignado'] = True
                    data['sku_match'] = match['sku_match']
                    data['fuente_catalogo'] = match['catalogo']
    
    if not resultados:
        st.warning(f"❌ No se encontraron resultados para: '{desc_buscar}'")
        return

    resultados_lista = list(resultados.values())
    resultados_lista.sort(key=lambda x: x['similitud'], reverse=True)
    st.success(f"✅ {len(resultados_lista)} SKUs encontrados")
    
    for i in range(0, len(resultados_lista), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(resultados_lista):
                r = resultados_lista[idx]
                stock_inmediato = r['stock_yessica'] + r['stock_apri004']
                if stock_inmediato > 0: color, estado = "#4CAF50", "✅ STOCK INMEDIATO"
                elif r['stock_apri001'] > 0: color, estado = "#FF9800", "⚠️ STOCK REMOTO"
                else: color, estado = "#f44336", "❌ SIN STOCK"
                
                with col:
                    precio_nota = ""
                    if r.get('precio_asignado') and r.get('sku_match') and r['sku_match'] != r['sku']:
                        precio_nota = f'<div style="background:#FFF3E0; border-radius:8px; padding:4px; margin:6px 0; font-size:10px; color:#e67e22;">⚠️ Precio desde SKU: {r["sku_match"]}</div>'
                    
                    st.markdown(f"""
                    <div style="background:#ffffff; border-radius:12px; padding:10px; margin-bottom:10px; border-left:4px solid {color}; box-shadow:0 1px 3px rgba(0,0,0,0.1);">
                        <div style="display:flex; justify-content:space-between;">
                            <b style="color:#1a1a2e;">📦 {r['sku']}</b>
                            <span style="background:{color}; color:white; padding:2px 8px; border-radius:12px; font-size:10px;">{estado}</span>
                        </div>
                        <p style="color:#333; font-size:11px;">📝 {r['descripcion'][:80]}</p>
                        <div style="display:flex; gap:8px; margin:5px 0;">
                            <span style="background:#4CAF50; color:white; padding:2px 6px; border-radius:10px;">🟢 Y: {r['stock_yessica']}</span>
                            <span style="background:#FF9800; color:white; padding:2px 6px; border-radius:10px;">🟡 A4: {r['stock_apri004']}</span>
                            <span style="background:#f44336; color:white; padding:2px 6px; border-radius:10px;">🔴 A1: {r['stock_apri001']}</span>
                        </div>
                        {precio_nota}
                        <p style="color:#e67e22; font-weight:bold;">💰 S/ {r['precio']:.2f}</p>
                    </div>
                    """, unsafe_allow_html=True)


def buscar_sku_exacto(sku_buscar, catalogos, stocks):
    """Busca un SKU específico - PERMITE PRECIO MANUAL"""
    sku_limpio = sku_buscar.strip().upper()
    descripcion = f"SKU: {sku_limpio}"
    precio_automatico = 0
    fuente_precio = None
    sku_match = None
    
    # Buscar descripción en catálogos
    for cat in catalogos:
        df = cat['df']
        col_sku = cat['col_sku']
        col_desc = cat.get('col_desc')
        mask = df[col_sku].astype(str).str.strip().str.upper() == sku_limpio
        if mask.any():
            row = df[mask].iloc[0]
            if col_desc:
                descripcion = str(row[col_desc])[:200]
            break
    
    # Buscar precio automático por descripción
    precio_key = st.session_state.get('precio_key', 'P. VIP')
    match = buscar_por_descripcion_en_catalogos(descripcion, catalogos, precio_key)
    
    if match['precio'] > 0:
        precio_automatico = match['precio']
        fuente_precio = match['catalogo']
        sku_match = match['sku_match']
    
    # Buscar stock en todas las hojas
    stock_yessica = 0
    stock_apri004 = 0
    stock_apri001 = 0
    
    for stock in stocks:
        df = stock['df']
        col_sku = stock['col_sku']
        hoja = stock.get('hoja', '')
        
        # Detectar columna de cantidad
        col_cant = None
        for col in df.columns:
            if any(p in str(col).upper() for p in ['CANT', 'STOCK', 'DISPONIBLE']):
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
    
    # Determinar color del borde
    if stock_inmediato > 0:
        color = "#4CAF50"
        estado = "✅ STOCK INMEDIATO"
    elif stock_apri001 > 0:
        color = "#FF9800"
        estado = "⚠️ STOCK REMOTO (APRI.001)"
    else:
        color = "#f44336"
        estado = "❌ SIN STOCK"
    
    # ========== MOSTRAR CARD DEL PRODUCTO ==========
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
    </div>
    """, unsafe_allow_html=True)
    
    # ========== SECCIÓN DE PRECIO (AUTOMÁTICO + MANUAL) ==========
    st.markdown("---")
    st.markdown("### 💰 Configurar Precio")
    
    col_p1, col_p2 = st.columns(2)
    
    with col_p1:
        if precio_automatico > 0:
            st.success(f"🤖 **Precio automático sugerido:** S/ {precio_automatico:.2f}")
            if sku_match and sku_match != sku_limpio:
                st.caption(f"📚 Desde SKU: {sku_match} | Fuente: {fuente_precio}")
            else:
                st.caption(f"📚 Fuente: {fuente_precio}")
        else:
            st.warning("🤖 **No se encontró precio automático**")
            st.caption("💡 Puedes ingresar el precio manualmente abajo")
    
    with col_p2:
        # Valor por defecto: precio automático si existe, sino 0
        valor_defecto = precio_automatico if precio_automatico > 0 else 0.0
        precio_manual = st.number_input(
            "✏️ **Precio manual (S/)**", 
            min_value=0.0, 
            max_value=500.0, 
            value=float(valor_defecto),
            step=1.0,
            key=f"manual_price_{sku_limpio}",
            help="Ingresa el precio correcto si el automático no es válido o no existe"
        )
    
    # Mostrar precio que se va a usar
    precio_final = precio_manual if precio_manual > 0 else precio_automatico
    st.markdown(f"""
    <div style="background:#e8f5e9; border-radius:10px; padding:10px; text-align:center; margin:10px 0;">
        <span style="font-size:14px;">💰 Precio a aplicar:</span>
        <span style="font-size:24px; font-weight:bold; color:#e67e22;"> S/ {precio_final:.2f}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # ========== BOTONES DE ACCIÓN ==========
    st.markdown("---")
    col_b1, col_b2, col_b3 = st.columns(3)
    
    with col_b1:
        if st.button(f"➕ Agregar al carrito", type="primary", use_container_width=True):
            if precio_final > 0:
                item = {
                    'sku': sku_limpio,
                    'descripcion': descripcion,
                    'cantidad': 1,
                    'precio': precio_final,
                    'total': precio_final,
                    'stock_yessica': stock_yessica,
                    'stock_apri004': stock_apri004,
                    'stock_apri001': stock_apri001
                }
                if 'carrito' not in st.session_state:
                    st.session_state.carrito = []
                st.session_state.carrito.append(item)
                st.success(f"✅ 1x {sku_limpio} agregado a S/ {precio_final:.2f}")
                st.rerun()
            else:
                st.error("❌ Ingresa un precio válido antes de agregar")
    
    with col_b2:
        # Seleccionar cantidad si tiene stock
        if stock_inmediato > 0 or stock_apri001 > 0:
            max_cant = stock_inmediato if stock_inmediato > 0 else stock_apri001
            with st.expander("📦 Agregar con cantidad específica", expanded=False):
                cantidad = st.number_input("Cantidad", min_value=1, max_value=max_cant, value=1, step=1, key=f"qty_{sku_limpio}")
                if st.button(f"➕ Agregar {cantidad} unidades", key=f"add_qty_{sku_limpio}"):
                    if precio_final > 0:
                        item = {
                            'sku': sku_limpio,
                            'descripcion': descripcion,
                            'cantidad': cantidad,
                            'precio': precio_final,
                            'total': precio_final * cantidad,
                            'stock_yessica': stock_yessica,
                            'stock_apri004': stock_apri004,
                            'stock_apri001': stock_apri001
                        }
                        if 'carrito' not in st.session_state:
                            st.session_state.carrito = []
                        st.session_state.carrito.append(item)
                        st.success(f"✅ {cantidad}x {sku_limpio} agregado a S/ {precio_final:.2f} c/u")
                        st.rerun()
                    else:
                        st.error("❌ Ingresa un precio válido")
        else:
            st.warning("❌ Sin stock disponible")
    
    with col_b3:
        if st.button(f"📋 Enviar al MODO MASIVO", use_container_width=True):
            st.session_state.skus_para_procesar = [sku_limpio]
            st.success(f"✅ SKU {sku_limpio} enviado al MODO MASIVO")
