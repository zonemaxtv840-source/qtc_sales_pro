# ui/tabs/skuscraper_tab.py
import streamlit as st
import pandas as pd
from difflib import SequenceMatcher
from collections import defaultdict


def render_skuscraper_tab():
    st.markdown("### 🔧 SKU SCRAPER - Analizador de Catálogo y Stock")
    st.caption("Detecta SKUs duplicados y productos con misma descripción")
    st.caption("📌 Busca en: Catálogos + Stock (YESSICA, APRI.004, APRI.001)")
    
    # Verificar si hay datos cargados
    tiene_catalogos = st.session_state.get('catalogos', [])
    tiene_stocks = st.session_state.get('stocks', [])
    
    if not tiene_catalogos and not tiene_stocks:
        st.warning("⚠️ Primero carga catálogos de precios o reportes de stock en el sidebar")
        return
    
    # Mostrar resumen
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**📚 Catálogos:** {len(tiene_catalogos)}")
    with col2:
        st.markdown(f"**📦 Stock:** {len(tiene_stocks)} hojas")
    
    st.markdown("---")
    
    modo_busqueda = st.radio(
        "📌 Modo de análisis",
        ["🔍 Buscar por SKU", "📝 Buscar por descripción", "📊 Analizar duplicados"],
        horizontal=True
    )
    
    if modo_busqueda == "🔍 Buscar por SKU":
        buscar_por_sku(tiene_catalogos, tiene_stocks)
    elif modo_busqueda == "📝 Buscar por descripción":
        buscar_por_descripcion(tiene_catalogos, tiene_stocks)
    else:
        analizar_duplicados(tiene_catalogos, tiene_stocks)


def buscar_por_sku(catalogos, stocks):
    """Busca un SKU específico en catálogos y stock"""
    st.markdown("### 🔍 Búsqueda por SKU")
    
    sku_buscar = st.text_input("Ingresa el SKU", placeholder="Ej: RN9401276NA8")
    
    if sku_buscar and st.button("🔍 Buscar", type="primary"):
        sku_limpio = sku_buscar.strip().upper()
        resultados = []
        
        with st.spinner("Buscando..."):
            # 1. Buscar en CATÁLOGOS
            for cat in catalogos:
                df = cat['df']
                col_sku = cat['col_sku']
                col_desc = cat.get('col_desc')
                
                mask = df[col_sku].astype(str).str.strip().str.upper() == sku_limpio
                for _, row in df[mask].iterrows():
                    desc = str(row[col_desc])[:200] if col_desc else "Sin descripción"
                    precios = {}
                    for nivel, col_precio in cat.get('precios', {}).items():
                        try:
                            precios[nivel] = float(row[col_precio]) if pd.notna(row[col_precio]) else 0
                        except:
                            precios[nivel] = 0
                    
                    resultados.append({
                        'fuente': f"📚 {cat['nombre'][:25]}",
                        'sku': sku_limpio,
                        'descripcion': desc,
                        'precio_vip': precios.get('P. VIP', 0),
                        'precio_box': precios.get('P. BOX', 0),
                        'precio_ir': precios.get('P. IR', 0),
                        'cantidad': None,
                        'tipo': 'catalogo'
                    })
            
            # 2. Buscar en STOCK
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
                    if any(p in col_upper for p in ['DESC', 'DESCRIPCION', 'PRODUCTO']):
                        col_desc = col
                        break
                
                mask = df[col_sku].astype(str).str.strip().str.upper() == sku_limpio
                for _, row in df[mask].iterrows():
                    cantidad = 0
                    if col_cant and pd.notna(row[col_cant]):
                        try:
                            cantidad = int(float(row[col_cant]))
                        except:
                            cantidad = 0
                    
                    desc = str(row[col_desc])[:200] if col_desc and pd.notna(row[col_desc]) else f"Stock en {hoja}"
                    
                    resultados.append({
                        'fuente': f"📦 {hoja}",
                        'sku': sku_limpio,
                        'descripcion': desc,
                        'cantidad': cantidad,
                        'tipo': 'stock'
                    })
        
        if resultados:
            st.success(f"✅ {len(resultados)} resultados")
            
            # Mostrar en GRID (2 columnas)
            cols = st.columns(2)
            for idx, r in enumerate(resultados):
                with cols[idx % 2]:
                    if r['tipo'] == 'catalogo':
                        st.markdown(f"""
                        <div style="background:white; border-radius:16px; padding:1rem; margin-bottom:1rem; border-left:5px solid #2196F3; box-shadow:0 4px 12px rgba(0,0,0,0.1); height:100%;">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
                                <span style="font-family:monospace; font-weight:bold; background:#e3f2fd; padding:4px 12px; border-radius:8px; color:#1565c0; font-size:0.9rem;">📦 {r['sku']}</span>
                                <span style="background:#2196F3; color:white; padding:4px 12px; border-radius:25px; font-size:0.7rem; font-weight:bold;">{r['fuente']}</span>
                            </div>
                            <div style="font-size:0.85rem; color:#333; margin-bottom:0.75rem; line-height:1.4; min-height:60px;">
                                📝 {r['descripcion'][:120]}{'...' if len(r['descripcion']) > 120 else ''}
                            </div>
                            <div style="display:flex; flex-wrap:wrap; gap:1rem; font-size:0.85rem; color:#555; padding-top:0.75rem; border-top:1px solid #eee; margin-top:0.5rem;">
                                <span style="color:#555;">💰 <strong style="color:#1565c0; font-size:1rem;">S/ {r['precio_vip']:.2f}</strong> VIP</span>
                                <span style="color:#555;">📦 <strong style="color:#1565c0;">S/ {r['precio_box']:.2f}</strong> BOX</span>
                                <span style="color:#555;">🏷️ <strong style="color:#1565c0;">S/ {r['precio_ir']:.2f}</strong> IR</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        color_borde = "#4CAF50" if r['cantidad'] > 0 else "#f44336"
                        badge_text = "✅ Con stock" if r['cantidad'] > 0 else "❌ Sin stock"
                        
                        st.markdown(f"""
                        <div style="background:white; border-radius:16px; padding:1rem; margin-bottom:1rem; border-left:5px solid {color_borde}; box-shadow:0 4px 12px rgba(0,0,0,0.1); height:100%;">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
                                <span style="font-family:monospace; font-weight:bold; background:#e3f2fd; padding:4px 12px; border-radius:8px; color:#1565c0; font-size:0.9rem;">📦 {r['sku']}</span>
                                <span style="background:{color_borde}; color:white; padding:4px 12px; border-radius:25px; font-size:0.7rem; font-weight:bold;">{r['fuente']}</span>
                            </div>
                            <div style="font-size:0.85rem; color:#333; margin-bottom:0.75rem; line-height:1.4; min-height:60px;">
                                📝 {r['descripcion'][:120]}{'...' if len(r['descripcion']) > 120 else ''}
                            </div>
                            <div style="display:flex; justify-content:space-between; align-items:center; padding-top:0.75rem; border-top:1px solid #eee; margin-top:0.5rem;">
                                <span style="color:#555;">📊 <strong style="color:#1565c0; font-size:1.1rem;">{r['cantidad']}</strong> unidades</span>
                                <span style="background:{color_borde}; color:white; padding:4px 12px; border-radius:20px; font-size:0.7rem;">{badge_text}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Botón para enviar al Bulk
            skus_unicos = list(set([r['sku'] for r in resultados]))
            if st.button(f"📋 Enviar {len(skus_unicos)} SKU(s) al MODO MASIVO", use_container_width=True):
                st.session_state.skus_para_procesar = skus_unicos
                st.success(f"✅ {len(skus_unicos)} SKUs enviados al MODO MASIVO")
        else:
            st.error(f"❌ No se encontró el SKU: {sku_buscar}")


def buscar_por_descripcion(catalogos, stocks):
    """Busca por descripción en catálogos y stock"""
    st.markdown("### 📝 Búsqueda por descripción")
    
    desc_buscar = st.text_input("Ingresa la descripción", placeholder="Ej: Cargador USB-C")
    
    if desc_buscar and st.button("🔍 Buscar", type="primary"):
        desc_limpia = desc_buscar.strip().lower()
        resultados = []
        
        with st.spinner("Buscando..."):
            for cat in catalogos:
                df = cat['df']
                col_sku = cat['col_sku']
                col_desc = cat.get('col_desc')
                
                if col_desc:
                    for _, row in df.iterrows():
                        desc = str(row[col_desc]).lower()
                        if desc_limpia in desc:
                            resultados.append({
                                'fuente': f"📚 {cat['nombre'][:25]}",
                                'sku': str(row[col_sku]).strip(),
                                'descripcion': str(row[col_desc])[:150],
                                'tipo': 'catalogo'
                            })
            
            for stock in stocks:
                df = stock['df']
                col_sku = stock['col_sku']
                hoja = stock.get('hoja', 'Desconocida')
                
                col_desc = None
                for col in df.columns:
                    col_upper = str(col).upper()
                    if any(p in col_upper for p in ['DESC', 'DESCRIPCION', 'PRODUCTO']):
                        col_desc = col
                        break
                
                if col_desc:
                    for _, row in df.iterrows():
                        desc = str(row[col_desc]).lower()
                        if desc_limpia in desc:
                            resultados.append({
                                'fuente': f"📦 {hoja}",
                                'sku': str(row[col_sku]).strip(),
                                'descripcion': str(row[col_desc])[:150],
                                'tipo': 'stock'
                            })
        
        if resultados:
            st.success(f"✅ {len(resultados)} resultados")
            
            # Mostrar en GRID (2 columnas)
            cols = st.columns(2)
            for idx, r in enumerate(resultados):
                with cols[idx % 2]:
                    badge_color = "#2196F3" if r['tipo'] == 'catalogo' else "#FF9800"
                    badge_text = "Catálogo" if r['tipo'] == 'catalogo' else "Stock"
                    
                    st.markdown(f"""
                    <div style="background:white; border-radius:16px; padding:1rem; margin-bottom:1rem; border-left:5px solid {badge_color}; box-shadow:0 4px 12px rgba(0,0,0,0.1); height:100%;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
                            <span style="font-family:monospace; font-weight:bold; background:#e3f2fd; padding:4px 12px; border-radius:8px; color:#1565c0; font-size:0.9rem;">📦 {r['sku']}</span>
                            <span style="background:{badge_color}; color:white; padding:4px 12px; border-radius:25px; font-size:0.7rem; font-weight:bold;">{r['fuente']}</span>
                        </div>
                        <div style="font-size:0.85rem; color:#333; line-height:1.4; min-height:60px;">
                            📝 {r['descripcion'][:120]}{'...' if len(r['descripcion']) > 120 else ''}
                        </div>
                        <div style="margin-top:0.75rem; padding-top:0.5rem; border-top:1px solid #eee;">
                            <span style="color:#555; font-size:0.75rem;">🏷️ {badge_text}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            skus_unicos = list(set([r['sku'] for r in resultados]))
            if st.button(f"📋 Enviar {len(skus_unicos)} SKU(s) al MODO MASIVO", use_container_width=True):
                st.session_state.skus_para_procesar = skus_unicos
                st.success(f"✅ {len(skus_unicos)} SKUs enviados")
        else:
            st.warning("No se encontraron resultados")


def analizar_duplicados(catalogos, stocks):
    """Analiza descripciones duplicadas"""
    st.markdown("### 📊 Análisis de descripciones duplicadas")
    st.caption("Encuentra la misma descripción con diferentes SKUs")
    
    if st.button("🔍 Iniciar análisis", type="primary", use_container_width=True):
        with st.spinner("Analizando..."):
            descripciones = defaultdict(list)
            
            for cat in catalogos:
                df = cat['df']
                col_sku = cat['col_sku']
                col_desc = cat.get('col_desc')
                
                if col_desc:
                    for _, row in df.iterrows():
                        sku = str(row[col_sku]).strip()
                        desc = str(row[col_desc])[:150].strip()
                        if desc and desc != 'nan':
                            descripciones[desc].append({
                                'sku': sku,
                                'fuente': f"📚 {cat['nombre'][:25]}"
                            })
            
            for stock in stocks:
                df = stock['df']
                col_sku = stock['col_sku']
                hoja = stock.get('hoja', 'Desconocida')
                
                col_desc = None
                for col in df.columns:
                    col_upper = str(col).upper()
                    if any(p in col_upper for p in ['DESC', 'DESCRIPCION', 'PRODUCTO']):
                        col_desc = col
                        break
                
                if col_desc:
                    for _, row in df.iterrows():
                        sku = str(row[col_sku]).strip()
                        desc = str(row[col_desc])[:150].strip()
                        if desc and desc != 'nan':
                            descripciones[desc].append({
                                'sku': sku,
                                'fuente': f"📦 {hoja}"
                            })
            
            duplicadas = {desc: items for desc, items in descripciones.items() if len(items) > 1}
            
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#1a237e 0%,#283593 100%); border-radius:16px; padding:1.5rem; margin:1rem 0; text-align:center;">
                <h4 style="color:white; margin:0 0 0.5rem 0;">📊 Resumen</h4>
                <div style="display:flex; justify-content:space-around;">
                    <div><span style="color:white;">📝 Total</span><br><span style="font-size:2rem; font-weight:bold; color:#ff9800;">{len(descripciones)}</span></div>
                    <div><span style="color:white;">🔄 Duplicados</span><br><span style="font-size:2rem; font-weight:bold; color:#ff9800;">{len(duplicadas)}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if duplicadas:
                st.markdown("### 🔍 Descripciones con múltiples SKUs")
                
                for desc, items in list(duplicadas.items())[:20]:
                    skus_vistos = {}
                    for item in items:
                        if item['sku'] not in skus_vistos:
                            skus_vistos[item['sku']] = []
                        skus_vistos[item['sku']].append(item['fuente'])
                    
                    st.markdown(f"""
                    <div style="background:#FFF3E0; border-radius:12px; padding:1rem; margin-bottom:0.75rem; border-left:4px solid #FF9800;">
                        <div style="font-size:0.9rem; margin-bottom:0.5rem;"><strong>📝 {desc[:100]}</strong></div>
                        <div style="font-size:0.8rem;"><strong>🏷️ SKUs ({len(skus_vistos)}):</strong></div>
                        <div style="display:flex; flex-wrap:wrap; gap:0.5rem; margin-top:0.5rem;">
                            {''.join([f'<span style="background:#e3f2fd; padding:4px 10px; border-radius:8px; font-family:monospace; font-size:0.75rem;">{sku}</span>' for sku in list(skus_vistos.keys())[:8]])}
                            {f'<span style="background:#f0f0f0; padding:4px 10px; border-radius:8px; font-size:0.75rem;">+{len(skus_vistos)-8} más</span>' if len(skus_vistos) > 8 else ''}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                reporte_data = []
                for desc, items in duplicadas.items():
                    for item in items:
                        reporte_data.append({'descripcion': desc, 'sku': item['sku'], 'fuente': item['fuente']})
                
                if reporte_data:
                    df_reporte = pd.DataFrame(reporte_data)
                    csv = df_reporte.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Descargar reporte CSV",
                        data=csv,
                        file_name="reporte_duplicados.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            else:
                st.success("✅ No se encontraron duplicados")
