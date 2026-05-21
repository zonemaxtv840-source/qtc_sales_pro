# ui/tabs/skuscraper_tab.py
import streamlit as st
import pandas as pd
from collections import Counter
from difflib import SequenceMatcher


def render_skuscraper_tab():
    st.markdown("### 🔧 SKU SCRAPER - Analizador de Catálogo")
    st.caption("Detecta SKUs duplicados, variantes y productos con misma descripción")
    
    # Verificar si hay datos cargados
    if not st.session_state.get('catalogos', []):
        st.warning("⚠️ Primero carga catálogos de precios en el sidebar")
        st.info("📂 Ve al sidebar → Catálogos de precios → Sube tus archivos Excel")
        return
    
    # Mostrar resumen de catálogos cargados
    with st.expander("📊 Catálogos cargados", expanded=False):
        for cat in st.session_state.catalogos:
            st.markdown(f"- **{cat['nombre']}** | SKUs: {len(cat['df'])} | Col SKU: {cat['col_sku']}")
    
    st.markdown("---")
    
    # Opciones de búsqueda
    modo_busqueda = st.radio(
        "📌 Selecciona el modo de análisis",
        ["🔍 Buscar por SKU", "📝 Buscar por descripción", "📊 Analizar todos los duplicados"],
        horizontal=True
    )
    
    st.markdown("---")
    
    if modo_busqueda == "🔍 Buscar por SKU":
        buscar_por_sku()
    
    elif modo_busqueda == "📝 Buscar por descripción":
        buscar_por_descripcion()
    
    else:
        analizar_todos_duplicados()


def buscar_por_sku():
    """Busca un SKU específico y muestra todas sus variantes"""
    st.markdown("### 🔍 Búsqueda por SKU")
    st.caption("Encuentra un SKU y todas sus variantes en los catálogos")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        sku_buscar = st.text_input("Ingresa el SKU a buscar", placeholder="Ej: RN9401276NA8")
    
    with col2:
        busqueda_exacta = st.checkbox("Búsqueda exacta", value=True, help="Si está activado, busca coincidencia exacta. Si no, busca parcial")
    
    if sku_buscar and st.button("🔍 Buscar", type="primary", use_container_width=True):
        sku_limpio = sku_buscar.strip().upper()
        resultados = []
        
        with st.spinner("Buscando en catálogos..."):
            for cat in st.session_state.catalogos:
                df = cat['df']
                col_sku = cat['col_sku']
                col_desc = cat.get('col_desc')
                
                if busqueda_exacta:
                    mask = df[col_sku].astype(str).str.strip().str.upper() == sku_limpio
                else:
                    mask = df[col_sku].astype(str).str.contains(sku_limpio, case=False, na=False)
                
                coincidencias = df[mask]
                
                for _, row in coincidencias.iterrows():
                    sku = str(row[col_sku]).strip()
                    desc = str(row[col_desc])[:200] if col_desc else "Sin descripción"
                    
                    # Intentar obtener precio
                    precio = 0
                    if st.session_state.get('precio_key') in cat.get('precios', {}):
                        col_precio = cat['precios'][st.session_state.precio_key]
                        try:
                            precio = float(row[col_precio]) if pd.notna(row[col_precio]) else 0
                        except:
                            precio = 0
                    
                    resultados.append({
                        'catalogo': cat['nombre'][:30],
                        'sku': sku,
                        'descripcion': desc,
                        'precio': precio
                    })
        
        if resultados:
            st.success(f"✅ Se encontraron {len(resultados)} coincidencias")
            
            # Mostrar resultados en tabla
            df_resultados = pd.DataFrame(resultados)
            st.dataframe(df_resultados, use_container_width=True, height=300)
            
            # Estadísticas
            skus_unicos = list(set([r['sku'] for r in resultados]))
            desc_unicas = list(set([r['descripcion'] for r in resultados]))
            
            st.markdown(f"""
            <div style="background:rgba(0,0,0,0.3);border-radius:12px;padding:1rem;margin-top:1rem;">
                <div style="display:flex;justify-content:space-around;flex-wrap:wrap;">
                    <div>📦 Total SKUs encontrados: <strong>{len(resultados)}</strong></div>
                    <div>🏷️ SKUs únicos: <strong>{len(skus_unicos)}</strong></div>
                    <div>📝 Descripciones únicas: <strong>{len(desc_unicas)}</strong></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Mostrar descripciones diferentes para el mismo SKU
            if len(skus_unicos) == 1 and len(desc_unicas) > 1:
                st.warning(f"⚠️ El SKU **{skus_unicos[0]}** tiene {len(desc_unicas)} descripciones diferentes:")
                for desc in desc_unicas:
                    st.markdown(f"- {desc}")
            
            # Botón para enviar al Bulk
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"📋 Enviar SKUs únicos ({len(skus_unicos)}) al MODO MASIVO", use_container_width=True):
                    st.session_state.skus_para_procesar = skus_unicos
                    st.success(f"✅ {len(skus_unicos)} SKUs enviados al MODO MASIVO")
            
            with col2:
                if st.button(f"📋 Enviar TODOS los SKUs ({len(resultados)}) al MODO MASIVO", use_container_width=True):
                    st.session_state.skus_para_procesar = [r['sku'] for r in resultados]
                    st.success(f"✅ {len(resultados)} SKUs enviados al MODO MASIVO")
        else:
            st.error(f"❌ No se encontró el SKU: {sku_buscar}")


def buscar_por_descripcion():
    """Busca productos por descripción y muestra variantes"""
    st.markdown("### 📝 Búsqueda por descripción")
    st.caption("Encuentra todos los SKUs que coinciden con una descripción")
    
    desc_buscar = st.text_input("Ingresa la descripción a buscar", 
                                  placeholder="Ej: Cargador USB Type-C 33W")
    
    umbral = st.slider("🎯 Porcentaje de similitud", 50, 100, 70, 5, 
                       help="Porcentaje mínimo de coincidencia para considerar el resultado")
    
    if desc_buscar and st.button("🔍 Buscar", type="primary", use_container_width=True):
        desc_limpia = desc_buscar.strip().lower()
        resultados = []
        
        with st.spinner("Buscando en catálogos..."):
            for cat in st.session_state.catalogos:
                df = cat['df']
                col_sku = cat['col_sku']
                col_desc = cat.get('col_desc')
                
                if not col_desc:
                    continue
                
                for _, row in df.iterrows():
                    desc_catalogo = str(row[col_desc]).lower()
                    
                    # Calcular similitud
                    similitud = calcular_similitud(desc_limpia, desc_catalogo)
                    
                    if similitud >= umbral:
                        sku = str(row[col_sku]).strip()
                        desc = str(row[col_desc])[:200]
                        
                        # Obtener precio
                        precio = 0
                        if st.session_state.get('precio_key') in cat.get('precios', {}):
                            col_precio = cat['precios'][st.session_state.precio_key]
                            try:
                                precio = float(row[col_precio]) if pd.notna(row[col_precio]) else 0
                            except:
                                precio = 0
                        
                        resultados.append({
                            'catalogo': cat['nombre'][:30],
                            'sku': sku,
                            'descripcion': desc,
                            'similitud': f"{similitud:.0f}%",
                            'precio': precio
                        })
        
        if resultados:
            st.success(f"✅ Se encontraron {len(resultados)} productos con descripción similar")
            
            # Mostrar resultados
            df_resultados = pd.DataFrame(resultados)
            st.dataframe(df_resultados, use_container_width=True, height=400)
            
            # Análisis de agrupación
            st.markdown("---")
            st.markdown("### 📊 Análisis de agrupación por descripción")
            
            # Agrupar por descripción
            desc_group = {}
            for r in resultados:
                desc_key = r['descripcion'][:100]
                if desc_key not in desc_group:
                    desc_group[desc_key] = []
                desc_group[desc_key].append(r['sku'])
            
            # Mostrar grupos con múltiples SKUs
            grupos_mostrados = 0
            for desc, skus in desc_group.items():
                if len(skus) > 1:
                    st.markdown(f"""
                    <div style="background:#FFF3E0;border-radius:12px;padding:1rem;margin-bottom:1rem;">
                        <strong>📝 Descripción:</strong> {desc}<br>
                        <strong>🔢 Cantidad de SKUs diferentes:</strong> {len(skus)}<br>
                        <strong>🏷️ SKUs:</strong><br>
                        {chr(10).join([f'&nbsp;&nbsp;• `{s}`' for s in skus[:5]])}
                        {f'<br>&nbsp;&nbsp;... y {len(skus)-5} más' if len(skus) > 5 else ''}
                    </div>
                    """, unsafe_allow_html=True)
                    grupos_mostrados += 1
            
            if grupos_mostrados == 0:
                st.info("No se encontraron descripciones con múltiples SKUs")
            
            # Botón para enviar al Bulk
            skus_encontrados = list(set([r['sku'] for r in resultados]))
            if st.button(f"📋 Enviar {len(skus_encontrados)} SKUs únicos al MODO MASIVO", use_container_width=True):
                st.session_state.skus_para_procesar = skus_encontrados
                st.success(f"✅ {len(skus_encontrados)} SKUs enviados al MODO MASIVO")
        else:
            st.warning("No se encontraron productos con esa descripción")


def analizar_todos_duplicados():
    """Analiza todos los catálogos en busca de duplicados e inconsistencias"""
    st.markdown("### 📊 Análisis global de duplicados")
    st.caption("Escanea todo el catálogo y reporta SKUs con múltiples descripciones y descripciones con múltiples SKUs")
    
    if st.button("🔍 Iniciar análisis completo", type="primary", use_container_width=True):
        with st.spinner("Analizando catálogos... Este proceso puede tomar unos segundos..."):
            resultados_por_sku = {}
            resultados_por_desc = {}
            total_skus = 0
            total_registros = 0
            
            for cat in st.session_state.catalogos:
                df = cat['df']
                col_sku = cat['col_sku']
                col_desc = cat.get('col_desc')
                
                total_registros += len(df)
                
                # Análisis por SKU
                for _, row in df.iterrows():
                    sku = str(row[col_sku]).strip()
                    if sku:
                        total_skus += 1
                        if sku not in resultados_por_sku:
                            resultados_por_sku[sku] = []
                        if col_desc:
                            desc = str(row[col_desc])[:200]
                            resultados_por_sku[sku].append(desc)
                
                # Análisis por descripción
                if col_desc:
                    for _, row in df.iterrows():
                        desc = str(row[col_desc])[:200]
                        sku = str(row[col_sku]).strip()
                        if desc and desc != 'nan':
                            if desc not in resultados_por_desc:
                                resultados_por_desc[desc] = []
                            resultados_por_desc[desc].append(sku)
            
            # Detectar problemas
            skus_con_multiples_desc = {
                sku: list(set(descs)) for sku, descs in resultados_por_sku.items() 
                if len(set(descs)) > 1
            }
            
            desc_con_multiples_skus = {
                desc: list(set(skus)) for desc, skus in resultados_por_desc.items() 
                if len(set(skus)) > 1
            }
            
            # Resumen general
            st.markdown(f"""
            <div style="background:rgba(0,0,0,0.3);border-radius:12px;padding:1rem;margin-bottom:1rem;">
                <div style="display:flex;justify-content:space-around;flex-wrap:wrap;">
                    <div>📊 Total registros: <strong>{total_registros}</strong></div>
                    <div>📦 SKUs únicos: <strong>{len(resultados_por_sku)}</strong></div>
                    <div>⚠️ SKUs con múltiples descripciones: <strong style="color:#f44336;">{len(skus_con_multiples_desc)}</strong></div>
                    <div>🔄 Descripciones con múltiples SKUs: <strong style="color:#FF9800;">{len(desc_con_multiples_skus)}</strong></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # SKUs con múltiples descripciones
            if skus_con_multiples_desc:
                st.markdown("### ⚠️ SKUs que aparecen con diferentes descripciones")
                st.caption(f"Se encontraron {len(skus_con_multiples_desc)} SKUs con este problema")
                
                for sku, descs in list(skus_con_multiples_desc.items())[:15]:
                    with st.expander(f"🔴 SKU: {sku} - {len(descs)} descripciones diferentes"):
                        for i, desc in enumerate(descs, 1):
                            st.markdown(f"{i}. {desc}")
                
                if len(skus_con_multiples_desc) > 15:
                    st.info(f"... y {len(skus_con_multiples_desc) - 15} SKUs más")
            else:
                st.success("✅ No se encontraron SKUs con descripciones inconsistentes")
            
            st.markdown("---")
            
            # Descripciones con múltiples SKUs
            if desc_con_multiples_skus:
                st.markdown("### 🔄 Descripciones que tienen múltiples SKUs")
                st.caption(f"Se encontraron {len(desc_con_multiples_skus)} descripciones con este patrón")
                
                # Ordenar por cantidad de SKUs (mayor primero)
                desc_ordenadas = sorted(desc_con_multiples_skus.items(), key=lambda x: len(x[1]), reverse=True)
                
                for desc, skus in desc_ordenadas[:15]:
                    with st.expander(f"📝 {desc[:80]}... - {len(skus)} SKUs asociados"):
                        st.markdown("**SKUs relacionados:**")
                        # Mostrar SKUs en columnas
                        cols = st.columns(4)
                        for i, sku in enumerate(skus[:20]):
                            cols[i % 4].markdown(f"`{sku}`")
                        if len(skus) > 20:
                            st.markdown(f"... y {len(skus) - 20} SKUs más")
                
                if len(desc_con_multiples_skus) > 15:
                    st.info(f"... y {len(desc_con_multiples_skus) - 15} descripciones más")
                
                # Sugerencia
                st.info("💡 **Sugerencia:** Las descripciones con múltiples SKUs podrían ser productos similares o variantes del mismo producto. Revisa si deberían unificarse.")
            else:
                st.success("✅ No se encontraron descripciones con múltiples SKUs")
            
            # Botón para exportar reporte
            if skus_con_multiples_desc or desc_con_multiples_skus:
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📋 Enviar SKUs problemáticos al MODO MASIVO", use_container_width=True):
                        skus_problematicos = list(skus_con_multiples_desc.keys())
                        st.session_state.skus_para_procesar = skus_problematicos
                        st.success(f"✅ {len(skus_problematicos)} SKUs enviados al MODO MASIVO")
                
                with col2:
                    # Crear reporte descargable
                    reporte_data = []
                    for sku, descs in skus_con_multiples_desc.items():
                        for desc in descs:
                            reporte_data.append({'SKU': sku, 'descripcion': desc, 'tipo': 'SKU con múltiples descripciones'})
                    
                    for desc, skus in desc_con_multiples_skus.items():
                        for sku in skus:
                            reporte_data.append({'SKU': sku, 'descripcion': desc, 'tipo': 'Descripción con múltiples SKUs'})
                    
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


def calcular_similitud(texto1: str, texto2: str) -> float:
    """Calcula similitud entre dos textos usando SequenceMatcher"""
    if not texto1 or not texto2:
        return 0.0
    
    texto1 = texto1.lower().strip()
    texto2 = texto2.lower().strip()
    
    if texto1 == texto2:
        return 100.0
    
    # Usar SequenceMatcher para similitud de secuencias
    return SequenceMatcher(None, texto1, texto2).ratio() * 100
