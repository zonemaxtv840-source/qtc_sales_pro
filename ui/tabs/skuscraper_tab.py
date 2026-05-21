# ui/tabs/skuscraper_tab.py
import streamlit as st
import pandas as pd
from difflib import SequenceMatcher
from collections import defaultdict
import re

# ==========================================
# CONFIGURACIÓN DE SEGURIDAD PARA PRECIOS
# ==========================================
# Definimos rangos de precio MÁXIMO por categoría de producto para evitar cruces ridículos
PRICE_LIMITS = {
    "EARPHONE": 80,      # Audífonos cableados no pueden costar 140 soles (a menos que sean muy pro, pero por seguridad)
    "CABLE": 50,
    "CHARGER": 150,
    "SPEAKER": 300,
    "WATCH": 400,
    "DEFAULT": 500
}

def get_product_family(description):
    """Detecta la familia del producto para aplicar el límite de precio correcto"""
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
    """
    Busca precio por descripción con FILTROS DE SEGURIDAD:
    1. Similitud mínima 85% (muy alta para evitar errores)
    2. Coherencia de familia de producto
    3. Límite de precio máximo según categoría
    """
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
            
            # 1. VERIFICAR SIMILITUD (Mínimo 85% para ser considerado el mismo producto)
            similitud = calcular_similitud(desc_buscar, desc_cat)
            if similitud < 85:  # UMBRAL ALTÍSIMO -> SOLO TEXTOS CASI IGUALES
                continue
            
            # 2. VERIFICAR COLOR (Si el original tiene color, el match debe tener el mismo)
            if color:
                if color.lower() not in desc_cat:
                    continue
            
            # 3. VERIFICAR FAMILIA (No cruzar un TV Stick con unos Audífonos)
            familia_match = get_product_family(desc_cat)
            if familia_match != familia_origen:
                # Si las familias NO coinciden, descartamos automáticamente
                continue
            
            # 4. OBTENER PRECIO Y VALIDAR RANGO
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
    
    # Ordenar por similitud y devolver el mejor
    if mejores_matches:
        mejores_matches.sort(key=lambda x: x['similitud'], reverse=True)
        return mejores_matches[0]
    
    return {'precio': 0, 'sku_match': None, 'similitud': 0, 'catalogo': None}


def render_skuscraper_tab():
    st.markdown("### 🔧 SKU SCRAPER - Buscador de Alternativas")
    st.caption("🔍 Encuentra TODOS los SKUs con la MISMA DESCRIPCIÓN")
    st.caption("⚠️ **Seguridad activada**: Solo cruza productos de la misma familia y con precio lógico.")
    
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
    st.markdown("### 🔍 O búsqueda por SKU exacto")
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
        
        # ========== 3. BUSCAR PRECIO POR DESCRIPCIÓN (CON SEGURIDAD) ==========
        precio_key = st.session_state.get('precio_key', 'P. VIP')
        for sku, data in resultados.items():
            if data['precio'] == 0 and data['descripcion']:
                match = buscar_por_descripcion_en_catalogos(data['descripcion'], catalogos, precio_key)
                if match['precio'] > 0:
                    data['precio'] = match['precio']
                    data['precio_asignado'] = True
                    data['sku_match'] = match['sku_match']
                    data['fuente_catalogo'] = match['catalogo']
    
    # --- MOSTRAR RESULTADOS ---
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
                        precio_nota = f'<div style="background:#FFF3E0; border-radius:8px; padding:4px; margin:6px 0; font-size:10px; color:#e67e22;">⚠️ Precio asignado desde SKU: {r["sku_match"]}</div>'
                    
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
    """Busca un SKU específico en catálogos y stock (VERSIÓN SEGURA)"""
    sku_limpio = sku_buscar.strip().upper()
    descripcion = f"SKU: {sku_limpio}"
    precio = 0
    fuente_precio = None
    precio_asignado = False
    sku_match = None
    
    # 1. Buscar en catálogos
    for cat in catalogos:
        df = cat['df']; col_sku = cat['col_sku']; col_desc = cat.get('col_desc')
        mask = df[col_sku].astype(str).str.strip().str.upper() == sku_limpio
        if mask.any():
            row = df[mask].iloc[0]
            if col_desc: descripcion = str(row[col_desc])[:200]
            precio_key = st.session_state.get('precio_key', 'P. VIP')
            if precio_key in cat.get('precios', {}):
                col_precio = cat['precios'][precio_key]
                try: precio = float(row[col_precio]) if pd.notna(row[col_precio]) else 0
                except: pass
                fuente_precio = cat['nombre'][:30]
            break
    
    # 2. Si no hay precio, buscar por descripción (CON SEGURIDAD)
    if precio == 0 and descripcion != f"SKU: {sku_limpio}":
        match = buscar_por_descripcion_en_catalogos(descripcion, catalogos, st.session_state.get('precio_key', 'P. VIP'))
        if match['precio'] > 0:
            precio = match['precio']
            fuente_precio = match['catalogo']
            precio_asignado = True
            sku_match = match['sku_match']
    
    # 3. Buscar stock...
    stock_yessica = stock_apri004 = stock_apri001 = 0
    for stock in stocks:
        df = stock['df']; col_sku = stock['col_sku']; hoja = stock.get('hoja', '')
        col_cant = None
        for col in df.columns:
            if any(p in str(col).upper() for p in ['CANT', 'STOCK', 'DISPONIBLE']):
                col_cant = col; break
        if not col_cant: continue
        mask = df[col_sku].astype(str).str.strip().str.upper() == sku_limpio
        if mask.any():
            row = df[mask].iloc[0]
            cantidad = int(row[col_cant]) if col_cant and pd.notna(row[col_cant]) else 0
            if 'YESSICA' in hoja.upper(): stock_yessica = cantidad
            elif 'APRI.004' in hoja.upper(): stock_apri004 = cantidad
            elif 'APRI.001' in hoja.upper(): stock_apri001 = cantidad
    
    # 4. Mostrar resultado
    st.markdown(f"""
    <div style="background:#ffffff; border-radius:12px; padding:15px; margin-top:10px; border-left:4px solid #4CAF50;">
        <b>📦 {sku_limpio}</b>
        <p>📝 {descripcion}</p>
        <div>🟢 YESSICA: {stock_yessica} | 🟡 APRI.004: {stock_apri004} | 🔴 APRI.001: {stock_apri001}</div>
        <p style="color:#e67e22; font-weight:bold;">💰 S/ {precio:.2f}</p>
        <p>📚 Fuente: {fuente_precio}</p>
        {f'<p style="color:red;">⚠️ PRECIO ASIGNADO DESDE OTRO SKU: {sku_match}</p>' if precio_asignado else ''}
    </div>
    """, unsafe_allow_html=True)
