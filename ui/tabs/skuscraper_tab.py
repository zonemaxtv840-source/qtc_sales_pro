# ui/tabs/skuscraper_tab.py
import streamlit as st
import pandas as pd
from difflib import SequenceMatcher
from collections import defaultdict


def render_skuscraper_tab():
    st.markdown("### 🔧 SKU SCRAPER - Buscador de Alternativas")
    st.caption("🔍 Encuentra SKUs con descripción SIMILAR (no necesita coincidencia exacta)")
    st.caption("📌 **YESSICA / APRI.004** = Stock inmediato | **APRI.001** = Última opción")
    
    tiene_catalogos = st.session_state.get('catalogos', [])
    tiene_stocks = st.session_state.get('stocks', [])
    
    if not tiene_catalogos:
        st.warning("⚠️ Primero carga catálogos de precios en el sidebar")
        return
    
    st.markdown("---")
    
    # Configuración de búsqueda
    col1, col2 = st.columns([3, 1])
    with col1:
        desc_buscar = st.text_input("🔍 Descripción del producto", placeholder="Ej: Type-C earphones, cargador 33W, cable USB")
    with col2:
        umbral_similitud = st.slider("🎯 % Similitud", 50, 100, 65, 5, 
                                      help="Porcentaje mínimo de coincidencia. 65% es recomendado para encontrar variantes")
    
    if desc_buscar and st.button("🔍 Buscar alternativas", type="primary"):
        buscar_alternativas(desc_buscar, umbral_similitud, tiene_catalogos, tiene_stocks)
    
    # También mantener búsqueda por SKU exacto
    st.markdown("---")
    st.markdown("### 🔍 O búsqueda por SKU exacto")
    sku_buscar = st.text_input("SKU exacto", placeholder="Ej: RN9401276NA8")
    if sku_buscar and st.button("🔍 Buscar SKU", type="secondary"):
        buscar_sku_exacto(sku_buscar, tiene_catalogos, tiene_stocks)


def calcular_similitud(texto1: str, texto2: str) -> float:
    """Calcula similitud entre dos textos (0-100)"""
    if not texto1 or not texto2:
        return 0.0
    
    texto1 = texto1.lower().strip()
    texto2 = texto2.lower().strip()
    
    if texto1 == texto2:
        return 100.0
    
    # Usar SequenceMatcher para similitud de secuencias
    return SequenceMatcher(None, texto1, texto2).ratio() * 100


def buscar_alternativas(desc_buscar, umbral, catalogos, stocks):
    """Busca SKUs con descripción SIMILAR"""
    desc_limpia = desc_buscar.strip().lower()
    resultados = []
    todos_los_skus = []
    
    with st.spinner(f"Buscando SKUs con similitud ≥ {umbral}%..."):
        # Buscar en catálogos por similitud de descripción
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
                    todos_los_skus.append(sku)
                    
                    # Obtener precio
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
                        'descripcion': str(row[col_desc])[:200],
                        'precio': precio,
                        'similitud': similitud,
                        'catalogo': cat['nombre'][:25]
                    })
    
    if not resultados:
        st.warning(f"❌ No se encontraron SKUs con similitud ≥ {umbral}% para: '{desc_buscar}'")
        st.info("💡 **Tips:**\n- Prueba con palabras más genéricas (ej: 'earphones' en lugar de 'type-c earphones black')\n- Baja el porcentaje de similitud\n- Busca por SKU exacto si lo conoces")
        return
    
    # Ordenar por similitud (mayor primero)
    resultados.sort(key=lambda x: x['similitud'], reverse=True)
    
    # Mostrar resumen
    st.success(f"✅ Se encontraron {len(resultados)} SKUs con similitud ≥ {umbral}%")
    
    # Mostrar la búsqueda que se usó
    st.markdown(f"""
    <div style="background:#e3f2fd; border-radius:10px; padding:0.5rem 1rem; margin-bottom:1rem;">
        <span style="color:#1565c0;">🔍 Búsqueda: <strong>"{desc_buscar}"</strong> | Umbral: {umbral}%</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Mostrar resultados en cards
    for r in resultados:
        sku = r['sku']
        
        # Buscar stock en cada hoja por separado
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
                
                if 'YESSICA' in hoja.upper():
                    stock_yessica = cantidad
                elif 'APRI.004' in hoja.upper():
                    stock_apri004 = cantidad
                elif 'APRI.001' in hoja.upper():
                    stock_apri001 = cantidad
        
        stock_inmediato = stock_yessica + stock_apri004
        
        # Determinar color y mensaje
        if stock_inmediato > 0:
            color_borde = "#4CAF50"
            estado = "✅ STOCK INMEDIATO"
            estado_color = "#4CAF50"
        elif stock_apri001 > 0:
            color_borde = "#FF9800"
            estado = "⚠️ STOCK REMOTO (APRI.001)"
            estado_color = "#FF9800"
        else:
            color_borde = "#f44336"
            estado = "❌ SIN STOCK"
            estado_color = "#f44336"
        
        # Barra de similitud visual
        similitud_bar = f"""
        <div style="background:#e0e0e0; border-radius:10px; height:6px; width:100%; margin-top:4px;">
            <div style="background:#2196F3; border-radius:10px; height:6px; width:{r['similitud']}%;"></div>
        </div>
        """
        
        st.markdown(f"""
        <div style="background:white; border-radius:16px; padding:1rem; margin-bottom:1rem; border-left:5px solid {color_borde}; box-shadow:0 2px 8px rgba(0,0,0,0.1);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                <div>
                    <span style="font-family:monospace; font-weight:bold; background:#e3f2fd; padding:4px 12px; border-radius:8px; color:#1565c0; font-size:0.9rem;">📦 {sku}</span>
                    <span style="margin-left:8px; font-size:0.7rem; color:#666;">🎯 {r['similitud']:.0f}% coincidencia</span>
                </div>
                <span style="background:{estado_color}; color:white; padding:4px 12px; border-radius:20px; font-size:0.7rem; font-weight:bold;">{estado}</span>
            </div>
            {similitud_bar}
            <div style="font-size:0.85rem; color:#333; margin-top:0.75rem; margin-bottom:0.75rem; line-height:1.4;">
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
            if stock_inmediato > 0:
                max_cantidad = stock_inmediato
                ayuda = f"Máximo disponible en stock inmediato: {stock_inmediato} unidades"
            elif stock_apri001 > 0:
                max_cantidad = stock_apri001
                ayuda = f"Máximo disponible en APRI.001: {stock_apri001} unidades (solicitar al almacén)"
            else:
                max_cantidad = 0
                ayuda = "No hay stock disponible"
            
            cantidad = st.number_input(
                f"Cantidad",
                min_value=0,
                max_value=max_cantidad if max_cantidad > 0 else 1,
                value=0,
                step=1,
                key=f"cant_{sku}",
                help=ayuda,
                disabled=max_cantidad == 0,
                label_visibility="collapsed"
            )
        with col2:
            if cantidad > 0 and st.button(f"➕ Agregar", key=f"add_{sku}", use_container_width=True):
                item = {
                    'sku': sku,
                    'descripcion': r['descripcion'],
                    'cantidad': cantidad,
                    'precio': r['precio'],
                    'total': r['precio'] * cantidad,
                    'stock_yessica': stock_yessica,
                    'stock_apri004': stock_apri004,
                    'stock_apri001': stock_apri001,
                    'tipo_stock': 'inmediato' if stock_inmediato > 0 else 'remoto'
                }
                if 'carrito' not in st.session_state:
                    st.session_state.carrito = []
                st.session_state.carrito.append(item)
                st.success(f"✅ Agregado: {cantidad}x {sku}")
                st.rerun()
        
        st.markdown("---")


def buscar_sku_exacto(sku_buscar, catalogos, stocks):
    """Busca un SKU específico (búsqueda exacta)"""
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
    </div>
    """, unsafe_allow_html=True)
