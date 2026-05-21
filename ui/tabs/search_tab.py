# ui/tabs/search_tab.py
import streamlit as st
import pandas as pd


def render_search_tab():
    st.markdown("### 🔍 Búsqueda Inteligente")
    st.caption("🔎 Busca por SKU, descripción, código de barras, modelo o marca")
    st.caption("📌 Muestra precios y stock en tiempo real")
    
    # Verificar datos cargados
    tiene_catalogos = st.session_state.get('catalogos', [])
    tiene_stocks = st.session_state.get('stocks', [])
    
    if not tiene_catalogos:
        st.warning("⚠️ Primero carga catálogos de precios en el sidebar")
        return
    
    # ========== FILTROS ==========
    st.markdown("### 📋 Filtros")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        busqueda = st.text_input("🔍 Buscar", placeholder="SKU, descripción, modelo...")
    
    with col_f2:
        # Obtener categorías únicas de los catálogos
        categorias = []
        for cat in tiene_catalogos:
            if 'Category' in cat['df'].columns:
                categorias.extend(cat['df']['Category'].dropna().unique().tolist())
        categorias = sorted(list(set(categorias)))
        if categorias:
            categoria_seleccionada = st.selectbox("📁 Categoría", ["Todas"] + categorias)
        else:
            categoria_seleccionada = "Todas"
            st.caption("💡 Categorías disponibles al cargar archivos con columna 'Category'")
    
    with col_f3:
        solo_con_stock = st.checkbox("📦 Solo productos con stock", value=False)
    
    st.markdown("---")
    
    # ========== BUSCAR EN CATÁLOGOS ==========
    if busqueda and len(busqueda) >= 2:
        busqueda_lower = busqueda.lower().strip()
        resultados = []
        
        with st.spinner("🔍 Buscando en catálogos y stock..."):
            
            for cat in tiene_catalogos:
                df = cat['df']
                col_sku = cat['col_sku']
                col_desc = cat.get('col_desc')
                
                # Filtrar por categoría
                df_filtrado = df
                if categoria_seleccionada != "Todas" and 'Category' in df.columns:
                    df_filtrado = df[df['Category'] == categoria_seleccionada]
                
                # Búsqueda en SKU
                mask_sku = df_filtrado[col_sku].astype(str).str.lower().str.contains(busqueda_lower, na=False)
                
                # Búsqueda en descripción
                mask_desc = pd.Series([False] * len(df_filtrado))
                if col_desc:
                    mask_desc = df_filtrado[col_desc].astype(str).str.lower().str.contains(busqueda_lower, na=False)
                
                mask = mask_sku | mask_desc
                
                for _, row in df_filtrado[mask].iterrows():
                    sku = str(row[col_sku]).strip()
                    descripcion = str(row[col_desc])[:150] if col_desc else f"SKU: {sku}"
                    
                    # Obtener precios
                    precios = {}
                    for nivel, col_precio in cat.get('precios', {}).items():
                        try:
                            precios[nivel] = float(row[col_precio]) if pd.notna(row[col_precio]) else 0
                        except:
                            precios[nivel] = 0
                    
                    # Obtener categoría
                    categoria = row['Category'] if 'Category' in df.columns else "General"
                    
                    resultados.append({
                        'cat_origen': cat['nombre'][:25],
                        'sku': sku,
                        'descripcion': descripcion,
                        'categoria': categoria,
                        'precios': precios,
                        'precio_vip': precios.get('P. VIP', 0),
                        'precio_box': precios.get('P. BOX', 0),
                        'precio_ir': precios.get('P. IR', 0),
                        'stock_yessica': 0,
                        'stock_apri004': 0,
                        'stock_apri001': 0
                    })
            
            # ========== AGREGAR STOCK A CADA RESULTADO ==========
            for r in resultados:
                sku = r['sku']
                
                for stock in tiene_stocks:
                    df_stock = stock['df']
                    col_sku_stock = stock['col_sku']
                    hoja = stock.get('hoja', '')
                    
                    # Detectar columna de cantidad
                    col_cant = None
                    for col in df_stock.columns:
                        if any(p in str(col).upper() for p in ['CANT', 'STOCK', 'DISPONIBLE']):
                            col_cant = col
                            break
                    
                    if not col_cant:
                        continue
                    
                    mask = df_stock[col_sku_stock].astype(str).str.strip().str.upper() == sku.upper()
                    if mask.any():
                        row = df_stock[mask].iloc[0]
                        cantidad = 0
                        if col_cant and pd.notna(row[col_cant]):
                            try:
                                cantidad = int(float(row[col_cant]))
                            except:
                                cantidad = 0
                        
                        if 'YESSICA' in hoja.upper():
                            r['stock_yessica'] += cantidad
                        elif 'APRI.004' in hoja.upper():
                            r['stock_apri004'] += cantidad
                        elif 'APRI.001' in hoja.upper():
                            r['stock_apri001'] += cantidad
            
            # Filtrar solo con stock si está activado
            if solo_con_stock:
                resultados = [r for r in resultados if r['stock_yessica'] + r['stock_apri004'] + r['stock_apri001'] > 0]
        
        # ========== MOSTRAR RESULTADOS ==========
        if resultados:
            st.success(f"✅ {len(resultados)} resultados encontrados")
            
            # Mostrar en grid de 2 columnas
            for i in range(0, len(resultados), 2):
                cols = st.columns(2)
                for j, col in enumerate(cols):
                    idx = i + j
                    if idx < len(resultados):
                        r = resultados[idx]
                        
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
                            <div style="background:#ffffff; border-radius:12px; padding:12px; margin-bottom:12px; border-left:4px solid {color}; box-shadow:0 1px 3px rgba(0,0,0,0.1);">
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                                    <b style="color:#1a1a2e; font-size:13px;">📦 {r['sku']}</b>
                                    <span style="background:{color}; color:#ffffff; padding:2px 8px; border-radius:12px; font-size:9px;">{estado}</span>
                                </div>
                                <p style="color:#333; font-size:11px; margin-bottom:8px;">📝 {r['descripcion'][:80]}</p>
                                <div style="display:flex; gap:6px; margin-bottom:8px; flex-wrap:wrap;">
                                    <span style="background:#e3f2fd; color:#1565c0; padding:2px 6px; border-radius:8px; font-size:9px;">🏷️ {r['categoria']}</span>
                                </div>
                                <div style="display:flex; gap:8px; margin-bottom:8px;">
                                    <span style="background:#4CAF50; color:white; padding:2px 6px; border-radius:10px; font-size:9px;">🟢 Y: {r['stock_yessica']}</span>
                                    <span style="background:#FF9800; color:white; padding:2px 6px; border-radius:10px; font-size:9px;">🟡 A4: {r['stock_apri004']}</span>
                                    <span style="background:#f44336; color:white; padding:2px 6px; border-radius:10px; font-size:9px;">🔴 A1: {r['stock_apri001']}</span>
                                </div>
                                <div style="display:flex; flex-wrap:wrap; gap:12px; margin:8px 0; padding:8px 0; border-top:1px solid #eee; border-bottom:1px solid #eee;">
                                    <span style="color:#555; font-size:11px;">💰 VIP: <strong style="color:#e67e22;">S/ {r['precio_vip']:.2f}</strong></span>
                                    <span style="color:#555; font-size:11px;">📦 BOX: <strong style="color:#e67e22;">S/ {r['precio_box']:.2f}</strong></span>
                                    <span style="color:#555; font-size:11px;">🏷️ IR: <strong style="color:#e67e22;">S/ {r['precio_ir']:.2f}</strong></span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Selector de cantidad y precio
                            nivel_precio = st.session_state.get('precio_key', 'P. VIP')
                            precio_seleccionado = r.get(f'precio_{nivel_precio.lower().replace(". ", "_")}', 0)
                            if nivel_precio == 'P. VIP':
                                precio_seleccionado = r['precio_vip']
                            elif nivel_precio == 'P. BOX':
                                precio_seleccionado = r['precio_box']
                            else:
                                precio_seleccionado = r['precio_ir']
                            
                            max_cant = stock_inmediato if stock_inmediato > 0 else r['stock_apri001']
                            if max_cant > 0 and precio_seleccionado > 0:
                                col_a, col_b = st.columns([2, 1])
                                with col_a:
                                    cantidad = st.number_input(
                                        "Cant", 
                                        min_value=0, 
                                        max_value=max_cant, 
                                        value=0, 
                                        step=1, 
                                        key=f"search_qty_{r['sku']}_{idx}",
                                        label_visibility="collapsed"
                                    )
                                with col_b:
                                    if cantidad > 0:
                                        if st.button(f"➕", key=f"search_add_{r['sku']}_{idx}"):
                                            item = {
                                                'sku': r['sku'],
                                                'descripcion': r['descripcion'],
                                                'cantidad': cantidad,
                                                'precio': precio_seleccionado,
                                                'total': precio_seleccionado * cantidad,
                                                'stock_yessica': r['stock_yessica'],
                                                'stock_apri004': r['stock_apri004'],
                                                'stock_apri001': r['stock_apri001']
                                            }
                                            if 'carrito' not in st.session_state:
                                                st.session_state.carrito = []
                                            st.session_state.carrito.append(item)
                                            st.success(f"✅ {cantidad}x {r['sku']} agregado")
                                            st.rerun()
                            elif max_cant > 0 and precio_seleccionado == 0:
                                st.caption("⚠️ Sin precio - No se puede cotizar")
                            else:
                                st.caption("❌ Sin stock disponible")
                            
                            st.markdown("<hr style='margin:8px 0;'>", unsafe_allow_html=True)
        else:
            st.info("No se encontraron productos. Prueba con otra búsqueda.")
    
    elif busqueda and len(busqueda) < 2:
        st.info("🔍 Escribe al menos 2 caracteres para buscar")
    
    else:
        st.info("🔍 Ingresa un SKU, descripción o modelo para comenzar la búsqueda")
