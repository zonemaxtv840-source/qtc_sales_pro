# ui/tabs/skuscraper_tab.py
import streamlit as st
import pandas as pd
from difflib import SequenceMatcher


def render_skuscraper_tab():
    st.markdown("### 🔧 SKU SCRAPER - Analizador de Catálogo y Stock")
    st.caption("Detecta SKUs duplicados, variantes y productos con misma descripción")
    st.caption("📌 Busca en: Catálogos de precios + Hojas de stock (YESSICA, APRI.004, APRI.001)")
    
    # Verificar si hay datos cargados
    tiene_catalogos = st.session_state.get('catalogos', [])
    tiene_stocks = st.session_state.get('stocks', [])
    
    if not tiene_catalogos and not tiene_stocks:
        st.warning("⚠️ Primero carga catálogos de precios o reportes de stock en el sidebar")
        st.info("📂 Ve al sidebar → Archivos → Carga tus archivos Excel")
        return
    
    # Mostrar resumen de datos cargados
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**📚 Catálogos:** {len(tiene_catalogos)} archivos")
        for cat in tiene_catalogos[:3]:
            st.caption(f"  - {cat['nombre'][:40]}")
    with col2:
        st.markdown(f"**📦 Stock:** {len(tiene_stocks)} hojas")
        for stock in tiene_stocks[:3]:
            st.caption(f"  - {stock['nombre'][:40]}")
    
    st.markdown("---")
    
    # Opciones de búsqueda
    modo_busqueda = st.radio(
        "📌 Selecciona el modo de análisis",
        ["🔍 Buscar por SKU", "📝 Buscar por descripción", "📊 Analizar todos los duplicados"],
        horizontal=True
    )
    
    st.markdown("---")
    
    if modo_busqueda == "🔍 Buscar por SKU":
        buscar_por_sku(tiene_catalogos, tiene_stocks)
    
    elif modo_busqueda == "📝 Buscar por descripción":
        buscar_por_descripcion(tiene_catalogos, tiene_stocks)
    
    else:
        analizar_todos_duplicados(tiene_catalogos, tiene_stocks)


def buscar_por_sku(catalogos, stocks):
    """Busca un SKU específico en catálogos y stock"""
    st.markdown("### 🔍 Búsqueda por SKU")
    st.caption("Encuentra un SKU en catálogos y verifica su stock")
    
    sku_buscar = st.text_input("Ingresa el SKU a buscar", placeholder="Ej: RN9401276NA8")
    
    if sku_buscar and st.button("🔍 Buscar", type="primary", use_container_width=True):
        sku_limpio = sku_buscar.strip().upper()
        resultados = []
        
        with st.spinner("Buscando en catálogos y stock..."):
            # 1. BÚSQUEDA EN CATÁLOGOS
            for cat in catalogos:
                df = cat['df']
                col_sku = cat['col_sku']
                col_desc = cat.get('col_desc')
                
                mask = df[col_sku].astype(str).str.strip().str.upper() == sku_limpio
                coincidencias = df[mask]
                
                for _, row in coincidencias.iterrows():
                    sku = str(row[col_sku]).strip()
                    desc = str(row[col_desc])[:200] if col_desc else "Sin descripción"
                    
                    # Obtener precios
                    precios = {}
                    for nivel, col_precio in cat.get('precios', {}).items():
                        try:
                            precios[nivel] = float(row[col_precio]) if pd.notna(row[col_precio]) else 0
                        except:
                            precios[nivel] = 0
                    
                    resultados.append({
                        'origen': f"📚 Catálogo: {cat['nombre'][:30]}",
                        'sku': sku,
                        'descripcion': desc,
                        'precio_vip': precios.get('P. VIP', 0),
                        'precio_box': precios.get('P. BOX', 0),
                        'precio_ir': precios.get('P. IR', 0),
                        'tipo': 'catalogo'
                    })
            
            # 2. BÚSQUEDA EN STOCK
            for stock in stocks:
                df = stock['df']
                col_sku = stock['col_sku']
                hoja = stock.get('hoja', 'Desconocida')
                
                mask = df[col_sku].astype(str).str.strip().str.upper() == sku_limpio
                coincidencias = df[mask]
                
                for _, row in coincidencias.iterrows():
                    sku = str(row[col_sku]).strip()
                    
                    # Buscar columna de cantidad
                    col_cant = None
                    for col in df.columns:
                        col_upper = str(col).upper()
                        if any(p in col_upper for p in ['CANT', 'STOCK', 'DISPONIBLE', 'UNIDADES']):
                            col_cant = col
                            break
                    
                    cantidad = 0
                    if col_cant:
                        try:
                            cantidad = int(float(row[col_cant])) if pd.notna(row[col_cant]) else 0
                        except:
                            cantidad = 0
                    
                    # Buscar descripción en stock si existe
                    desc_stock = ""
                    for col in df.columns:
                        col_upper = str(col).upper()
                        if any(p in col_upper for p in ['DESC', 'DESCRIPCION', 'PRODUCTO']):
                            desc_stock = str(row[col])[:200] if pd.notna(row[col]) else ""
                            break
                    
                    resultados.append({
                        'origen': f"📦 Stock: {hoja}",
                        'sku': sku,
                        'descripcion': desc_stock if desc_stock else f"Stock en {hoja}",
                        'cantidad': cantidad,
                        'tipo': 'stock'
                    })
        
        if resultados:
            st.success(f"✅ Se encontraron {len(resultados)} resultados")
            
            # Separar resultados por tipo
            resultados_catalogo = [r for r in resultados if r['tipo'] == 'catalogo']
            resultados_stock = [r for r in resultados if r['tipo'] == 'stock']
            
            # Mostrar resultados de catálogo
            if resultados_catalogo:
                st.markdown("#### 📚 En catálogos:")
                for r in resultados_catalogo:
                    st.markdown(f"""
                    <div style="background:white;border-radius:16px;padding:1rem;margin-bottom:1rem;border-left:5px solid #2196F3;">
                        <div style="display:flex;justify-content:space-between;">
                            <strong>📦 {r['sku']}</strong>
                            <span style="background:#2196F3;color:white;padding:4px 12px;border-radius:20px;">{r['origen']}</span>
                        </div>
                        <div style="margin-top:8px;">📝 {r['descripcion']}</div>
                        <div style="margin-top:8px;display:flex;gap:1rem;">
                            <span>💰 VIP: S/ {r['precio_vip']:.2f}</span>
                            <span>📦 BOX: S/ {r['precio_box']:.2f}</span>
                            <span>🏷️ IR: S/ {r['precio_ir']:.2f}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Mostrar resultados de stock
            if resultados_stock:
                st.markdown("#### 📦 En stock:")
                for r in resultados_stock:
                    color = "#4CAF50" if r.get('cantidad', 0) > 0 else "#f44336"
                    st.markdown(f"""
                    <div style="background:white;border-radius:16px;padding:1rem;margin-bottom:1rem;border-left:5px solid {color};">
                        <div style="display:flex;justify-content:space-between;">
                            <strong>📦 {r['sku']}</strong>
                            <span style="background:{color};color:white;padding:4px 12px;border-radius:20px;">{r['origen']}</span>
                        </div>
                        <div style="margin-top:8px;">📝 {r['descripcion']}</div>
                        <div style="margin-top:8px;">📊 Cantidad disponible: <strong>{r.get('cantidad', 0)}</strong></div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # SKUs para enviar al Bulk
            skus_unicos = list(set([r['sku'] for r in resultados]))
            if st.button(f"📋 Enviar {len(skus_unicos)} SKU(s) al MODO MASIVO", use_container_width=True):
                st.session_state.skus_para_procesar = skus_unicos
                st.success(f"✅ {len(skus_unicos)} SKUs enviados al MODO MASIVO")
        else:
            st.error(f"❌ No se encontró el SKU: {sku_buscar}")


def buscar_por_descripcion(catalogos, stocks):
    """Busca productos por descripción en catálogos y stock"""
    st.markdown("### 📝 Búsqueda por descripción")
    st.caption("Encuentra todos los SKUs que coinciden con una descripción")
    
    desc_buscar = st.text_input("Ingresa la descripción a buscar", 
                                  placeholder="Ej: Cargador USB Type-C")
    
    if desc_buscar and st.button("🔍 Buscar", type="primary", use_container_width=True):
        desc_limpia = desc_buscar.strip().lower()
        resultados = []
        
        with st.spinner("Buscando en catálogos y stock..."):
            # Búsqueda en catálogos
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
                        desc = str(row[col_desc])[:200]
                        
                        resultados.append({
                            'origen': f"📚 Catálogo: {cat['nombre'][:30]}",
                            'sku': sku,
                            'descripcion': desc,
                            'tipo': 'catalogo'
                        })
            
            # Búsqueda en stock
            for stock in stocks:
                df = stock['df']
                col_sku = stock['col_sku']
                hoja = stock.get('hoja', 'Desconocida')
                
                # Buscar columna de descripción en stock
                col_desc_stock = None
                for col in df.columns:
                    col_upper = str(col).upper()
                    if any(p in col_upper for p in ['DESC', 'DESCRIPCION', 'PRODUCTO']):
                        col_desc_stock = col
                        break
                
                if col_desc_stock:
                    for _, row in df.iterrows():
                        desc_stock = str(row[col_desc_stock]).lower()
                        if desc_limpia in desc_stock:
                            sku = str(row[col_sku]).strip()
                            desc = str(row[col_desc_stock])[:200]
                            
                            resultados.append({
                                'origen': f"📦 Stock: {hoja}",
                                'sku': sku,
                                'descripcion': desc,
                                'tipo': 'stock'
                            })
        
        if resultados:
            st.success(f"✅ Se encontraron {len(resultados)} productos")
            
            df_resultados = pd.DataFrame(resultados)
            st.dataframe(df_resultados, use_container_width=True, height=400)
            
            skus_unicos = list(set([r['sku'] for r in resultados]))
            if st.button(f"📋 Enviar {len(skus_unicos)} SKU(s) al MODO MASIVO", use_container_width=True):
                st.session_state.skus_para_procesar = skus_unicos
                st.success(f"✅ {len(skus_unicos)} SKUs enviados al MODO MASIVO")
        else:
            st.warning("No se encontraron productos con esa descripción")


def analizar_todos_duplicados(catalogos, stocks):
    """Analiza todos los catálogos y stock en busca de duplicados"""
    st.markdown("### 📊 Análisis global de duplicados")
    
    if st.button("🔍 Iniciar análisis completo", type="primary", use_container_width=True):
        with st.spinner("Analizando catálogos y stock..."):
            skus_por_descripcion = {}
            stock_por_sku = {}
            
            # Analizar catálogos
            for cat in catalogos:
                df = cat['df']
                col_sku = cat['col_sku']
                col_desc = cat.get('col_desc')
                
                if col_desc:
                    for _, row in df.iterrows():
                        sku = str(row[col_sku]).strip()
                        desc = str(row[col_desc])[:150]
                        if desc not in skus_por_descripcion:
                            skus_por_descripcion[desc] = []
                        if sku not in skus_por_descripcion[desc]:
                            skus_por_descripcion[desc].append(sku)
            
            # Analizar stock
            for stock in stocks:
                df = stock['df']
                col_sku = stock['col_sku']
                hoja = stock.get('hoja', 'Desconocida')
                
                # Buscar columna de cantidad
                col_cant = None
                for col in df.columns:
                    col_upper = str(col).upper()
                    if any(p in col_upper for p in ['CANT', 'STOCK', 'DISPONIBLE']):
                        col_cant = col
                        break
                
                for _, row in df.iterrows():
                    sku = str(row[col_sku]).strip()
                    cantidad = 0
                    if col_cant and pd.notna(row[col_cant]):
                        try:
                            cantidad = int(float(row[col_cant]))
                        except:
                            cantidad = 0
                    
                    if sku not in stock_por_sku:
                        stock_por_sku[sku] = {'total': 0, 'ubicaciones': []}
                    stock_por_sku[sku]['total'] += cantidad
                    stock_por_sku[sku]['ubicaciones'].append({'hoja': hoja, 'cantidad': cantidad})
            
            # Mostrar descripciones con múltiples SKUs
            desc_con_multiples = {desc: skus for desc, skus in skus_por_descripcion.items() if len(skus) > 1}
            
            st.markdown(f"""
            <div style="background:rgba(0,0,0,0.3);border-radius:12px;padding:1rem;margin-bottom:1rem;">
                <div style="display:flex;justify-content:space-around;">
                    <div>📚 Descripciones analizadas: <strong>{len(skus_por_descripcion)}</strong></div>
                    <div>🔄 Con múltiples SKUs: <strong style="color:#FF9800;">{len(desc_con_multiples)}</strong></div>
                    <div>📦 SKUs con stock: <strong>{len(stock_por_sku)}</strong></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Mostrar ejemplos
            if desc_con_multiples:
                st.markdown("### 🔄 Descripciones con múltiples SKUs")
                for desc, skus in list(desc_con_multiples.items())[:10]:
                    st.markdown(f"""
                    <div style="background:#FFF3E0;border-radius:12px;padding:1rem;margin-bottom:0.5rem;">
                        <strong>📝 {desc[:80]}</strong><br>
                        <strong>🏷️ SKUs ({len(skus)}):</strong> {', '.join(skus[:5])}{'...' if len(skus) > 5 else ''}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Mostrar resumen de stock
            if stock_por_sku:
                st.markdown("### 📦 Resumen de stock por SKU")
                stock_df = pd.DataFrame([
                    {'SKU': sku, 'Stock Total': info['total'], 'Ubicaciones': len(info['ubicaciones'])}
                    for sku, info in stock_por_sku.items()
                ]).sort_values('Stock Total', ascending=False).head(20)
                st.dataframe(stock_df, use_container_width=True)
