# ui/tabs/skuscraper_tab.py
import streamlit as st
import pandas as pd
from collections import defaultdict


def render_skuscraper_tab():
    st.markdown("### 🔧 SKU SCRAPER - Analizador de Catálogo y Stock")
    st.caption("Detecta SKUs duplicados y productos con misma descripción")
    
    tiene_catalogos = st.session_state.get('catalogos', [])
    tiene_stocks = st.session_state.get('stocks', [])
    
    if not tiene_catalogos and not tiene_stocks:
        st.warning("⚠️ Primero carga catálogos de precios o reportes de stock en el sidebar")
        return
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**📚 Catálogos:** {len(tiene_catalogos)}")
    with col2:
        st.markdown(f"**📦 Stock:** {len(tiene_stocks)} hojas")
    
    st.markdown("---")
    
    modo = st.radio(
        "📌 Modo de análisis",
        ["🔍 Buscar por SKU", "📝 Buscar por descripción", "📊 Analizar duplicados"],
        horizontal=True
    )
    
    if modo == "🔍 Buscar por SKU":
        buscar_por_sku(tiene_catalogos, tiene_stocks)
    elif modo == "📝 Buscar por descripción":
        buscar_por_descripcion(tiene_catalogos, tiene_stocks)
    else:
        analizar_duplicados(tiene_catalogos, tiene_stocks)


def buscar_por_sku(catalogos, stocks):
    st.markdown("### 🔍 Búsqueda por SKU")
    
    sku_buscar = st.text_input("Ingresa el SKU", placeholder="Ej: RN9401276NA8")
    
    if sku_buscar and st.button("🔍 Buscar", type="primary"):
        sku_limpio = sku_buscar.strip().upper()
        resultados = []
        
        with st.spinner("Buscando..."):
            # Buscar en catálogos
            for cat in catalogos:
                df = cat['df']
                col_sku = cat['col_sku']
                col_desc = cat.get('col_desc')
                
                mask = df[col_sku].astype(str).str.strip().str.upper() == sku_limpio
                for _, row in df[mask].iterrows():
                    desc = str(row[col_desc])[:200] if col_desc else "Sin descripción"
                    resultados.append({
                        'fuente': cat['nombre'][:25],
                        'sku': sku_limpio,
                        'descripcion': desc,
                        'tipo': 'catalogo',
                        'precio': float(row[cat['precios'].get('P. VIP', df.columns[0])]) if cat.get('precios') else 0
                    })
            
            # Buscar en stock
            for stock in stocks:
                df = stock['df']
                col_sku = stock['col_sku']
                hoja = stock.get('hoja', '')
                
                col_cant = None
                for col in df.columns:
                    if any(p in str(col).upper() for p in ['CANT', 'STOCK', 'DISPONIBLE']):
                        col_cant = col
                        break
                
                mask = df[col_sku].astype(str).str.strip().str.upper() == sku_limpio
                for _, row in df[mask].iterrows():
                    cantidad = int(row[col_cant]) if col_cant and pd.notna(row[col_cant]) else 0
                    resultados.append({
                        'fuente': hoja,
                        'sku': sku_limpio,
                        'descripcion': f"Stock en {hoja}",
                        'cantidad': cantidad,
                        'tipo': 'stock'
                    })
        
        if resultados:
            st.success(f"✅ {len(resultados)} resultados")
            
            # Mostrar en 2 columnas
            for i in range(0, len(resultados), 2):
                cols = st.columns(2)
                for j, col in enumerate(cols):
                    idx = i + j
                    if idx < len(resultados):
                        r = resultados[idx]
                        if r['tipo'] == 'catalogo':
                            with col:
                                st.markdown(f"""
                                <div style="background:white; border-radius:15px; padding:15px; margin-bottom:15px; border-left:5px solid #2196F3; box-shadow:0 2px 5px rgba(0,0,0,0.1);">
                                    <p style="margin:0 0 8px 0;"><strong style="color:#1565c0; font-size:16px;">📦 {r['sku']}</strong> <span style="background:#2196F3; color:white; padding:2px 8px; border-radius:15px; font-size:11px; margin-left:8px;">{r['fuente']}</span></p>
                                    <p style="margin:0 0 8px 0; color:#333; font-size:13px;">📝 {r['descripcion'][:80]}</p>
                                    <p style="margin:0; color:#555; font-size:13px;">💰 Precio: <strong style="color:#e67e22;">S/ {r['precio']:.2f}</strong></p>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            color = "#4CAF50" if r['cantidad'] > 0 else "#f44336"
                            with col:
                                st.markdown(f"""
                                <div style="background:white; border-radius:15px; padding:15px; margin-bottom:15px; border-left:5px solid {color}; box-shadow:0 2px 5px rgba(0,0,0,0.1);">
                                    <p style="margin:0 0 8px 0;"><strong style="color:#1565c0; font-size:16px;">📦 {r['sku']}</strong> <span style="background:{color}; color:white; padding:2px 8px; border-radius:15px; font-size:11px; margin-left:8px;">{r['fuente']}</span></p>
                                    <p style="margin:0 0 8px 0; color:#333; font-size:13px;">📝 {r['descripcion']}</p>
                                    <p style="margin:0; color:#555; font-size:13px;">📊 Cantidad: <strong style="color:#e67e22;">{r['cantidad']}</strong> unidades</p>
                                </div>
                                """, unsafe_allow_html=True)
            
            skus_unicos = list(set([r['sku'] for r in resultados]))
            if st.button(f"📋 Enviar {len(skus_unicos)} SKU(s) al MODO MASIVO", use_container_width=True):
                st.session_state.skus_para_procesar = skus_unicos
                st.success(f"✅ {len(skus_unicos)} SKUs enviados")
        else:
            st.error(f"❌ No se encontró el SKU: {sku_buscar}")


def buscar_por_descripcion(catalogos, stocks):
    st.markdown("### 📝 Búsqueda por descripción")
    
    desc_buscar = st.text_input("Ingresa la descripción", placeholder="Ej: Cargador")
    
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
                        if desc_limpia in str(row[col_desc]).lower():
                            resultados.append({
                                'sku': str(row[col_sku]).strip(),
                                'descripcion': str(row[col_desc])[:100],
                                'fuente': cat['nombre'][:25],
                                'tipo': 'catalogo'
                            })
            
            for stock in stocks:
                df = stock['df']
                col_sku = stock['col_sku']
                hoja = stock.get('hoja', '')
                col_desc = None
                for col in df.columns:
                    if any(p in str(col).upper() for p in ['DESC', 'DESCRIPCION']):
                        col_desc = col
                        break
                if col_desc:
                    for _, row in df.iterrows():
                        if desc_limpia in str(row[col_desc]).lower():
                            resultados.append({
                                'sku': str(row[col_sku]).strip(),
                                'descripcion': str(row[col_desc])[:100],
                                'fuente': hoja,
                                'tipo': 'stock'
                            })
        
        if resultados:
            st.success(f"✅ {len(resultados)} resultados")
            df_resultados = pd.DataFrame(resultados)
            st.dataframe(df_resultados, use_container_width=True)
            
            skus_unicos = list(set([r['sku'] for r in resultados]))
            if st.button(f"📋 Enviar {len(skus_unicos)} SKU(s) al MODO MASIVO", use_container_width=True):
                st.session_state.skus_para_procesar = skus_unicos
                st.success(f"✅ {len(skus_unicos)} SKUs enviados")
        else:
            st.warning("No se encontraron resultados")


def analizar_duplicados(catalogos, stocks):
    st.markdown("### 📊 Análisis de descripciones duplicadas")
    
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
                        desc = str(row[col_desc])[:100].strip()
                        if desc and desc != 'nan':
                            descripciones[desc].append(sku)
            
            for stock in stocks:
                df = stock['df']
                col_sku = stock['col_sku']
                col_desc = None
                for col in df.columns:
                    if any(p in str(col).upper() for p in ['DESC', 'DESCRIPCION']):
                        col_desc = col
                        break
                if col_desc:
                    for _, row in df.iterrows():
                        sku = str(row[col_sku]).strip()
                        desc = str(row[col_desc])[:100].strip()
                        if desc and desc != 'nan':
                            descripciones[desc].append(sku)
            
            duplicadas = {desc: list(set(skus)) for desc, skus in descripciones.items() if len(set(skus)) > 1}
            
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#1a237e,#283593); border-radius:15px; padding:15px; margin:10px 0; text-align:center;">
                <p style="color:white; margin:0;"><strong>📊 Total descripciones: {len(descripciones)}</strong></p>
                <p style="color:#ff9800; margin:5px 0 0 0;"><strong>🔄 Con múltiples SKUs: {len(duplicadas)}</strong></p>
            </div>
            """, unsafe_allow_html=True)
            
            if duplicadas:
                for desc, skus in list(duplicadas.items())[:20]:
                    st.markdown(f"""
                    <div style="background:#FFF3E0; border-radius:10px; padding:10px; margin-bottom:8px; border-left:3px solid #FF9800;">
                        <p style="margin:0 0 5px 0; color:#1a1a2e;"><strong>📝 {desc}</strong></p>
                        <p style="margin:0; color:#555; font-size:12px;"><strong>SKUs:</strong> {', '.join(skus[:5])}{'...' if len(skus) > 5 else ''}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                if st.button("📥 Exportar reporte", use_container_width=True):
                    reporte = []
                    for desc, skus in duplicadas.items():
                        for sku in skus:
                            reporte.append({'descripcion': desc, 'sku': sku})
                    df_reporte = pd.DataFrame(reporte)
                    csv = df_reporte.to_csv(index=False).encode('utf-8')
                    st.download_button("💾 Descargar CSV", data=csv, file_name="duplicados.csv")
            else:
                st.success("✅ No se encontraron duplicados")
