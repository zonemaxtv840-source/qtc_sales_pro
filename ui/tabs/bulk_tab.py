# ui/tabs/bulk_tab.py
import streamlit as st
import pandas as pd
from modules.stock_logic import calcular_cantidad_total, calcular_maximo_apri001, calcular_stock_seguro


def render_bulk_tab():
    st.markdown("### 📦 MODO MASIVO (Bulk)")
    st.caption("Procesa múltiples SKUs con sus cantidades para generar cotización")
    
    # Mostrar SKUs disponibles desde el Scraper
    skus_desde_scraper = st.session_state.get('skus_para_procesar', [])
    
    if skus_desde_scraper:
        st.info(f"🔗 **{len(skus_desde_scraper)} SKUs disponibles desde SKU SCRAPER**")
        if st.button("📋 Cargar SKUs desde Scraper", use_container_width=True):
            cargar_skus_desde_scraper(skus_desde_scraper)
    
    st.markdown("---")
    
    # Área de ingreso manual
    st.markdown("### ✏️ Ingreso manual")
    st.caption("Formato: `SKU:CANTIDAD` (uno por línea)")
    
    texto_bulk = st.text_area(
        "📝 Lista de productos",
        height=200,
        placeholder="Ejemplo:\nRN9401276NA8:100\nCN0200047BK8:50\nRN0200065BK8:25\nCN9406882NA8:10",
        help="Formato: SKU:CANTIDAD (uno por línea)"
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Procesar lista", type="primary", use_container_width=True):
            if texto_bulk.strip():
                procesar_texto_bulk(texto_bulk)
            else:
                st.warning("Ingresa productos en el formato SKU:CANTIDAD")
    
    with col2:
        if st.button("📋 Procesar desde Scraper", use_container_width=True):
            if skus_desde_scraper:
                procesar_skus_desde_scraper(skus_desde_scraper)
            else:
                st.warning("No hay SKUs en el Scraper. Ve al tab SKU SCRAPER primero")
    
    with col3:
        if st.button("🗑️ Limpiar todo", use_container_width=True):
            limpiar_todo()
    
    # Mostrar tabla de productos actuales
    if 'productos_actuales' in st.session_state and st.session_state.productos_actuales:
        st.markdown("---")
        st.markdown("### 📋 Productos en lista actual")
        mostrar_tabla_productos()
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Procesar y cotizar", type="primary", use_container_width=True):
                procesar_y_cotizar()
        with col2:
            if st.button("🗑️ Limpiar lista", use_container_width=True):
                st.session_state.productos_actuales = []
                if 'resultados_procesados' in st.session_state:
                    del st.session_state.resultados_procesados
                st.rerun()
    
    # Mostrar resultados del procesamiento
    if 'resultados_procesados' in st.session_state and st.session_state.resultados_procesados:
        st.markdown("---")
        st.markdown("### 📊 Resultados del procesamiento")
        mostrar_resultados_procesados()


def cargar_skus_desde_scraper(skus):
    """Carga SKUs desde el Scraper con cantidad por defecto = 1"""
    productos = []
    for sku in skus:
        productos.append({
            'sku': sku.strip().upper(),
            'cantidad': 1
        })
    st.session_state.productos_actuales = productos
    st.success(f"✅ Cargados {len(productos)} SKUs desde el Scraper (cantidad por defecto: 1)")
    st.rerun()


def procesar_texto_bulk(texto):
    """Procesa texto en formato SKU:CANTIDAD"""
    productos = []
    errores = []
    
    for line in texto.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
            
        if ':' in line:
            parts = line.split(':')
            if len(parts) == 2:
                try:
                    sku = parts[0].strip().upper()
                    cantidad = int(parts[1].strip())
                    if cantidad > 0:
                        productos.append({'sku': sku, 'cantidad': cantidad})
                    else:
                        errores.append(f"{line} - Cantidad debe ser mayor a 0")
                except ValueError:
                    errores.append(f"{line} - Cantidad inválida")
            else:
                errores.append(f"{line} - Formato incorrecto (usa SKU:CANTIDAD)")
        else:
            # Si solo tiene SKU, asignar cantidad 1 por defecto
            productos.append({'sku': line.strip().upper(), 'cantidad': 1})
    
    if errores:
        for error in errores[:5]:
            st.warning(error)
        if len(errores) > 5:
            st.warning(f"... y {len(errores) - 5} errores más")
    
    if productos:
        st.session_state.productos_actuales = productos
        st.success(f"✅ Cargados {len(productos)} productos")
        st.rerun()
    else:
        st.error("No se encontraron productos válidos")


def procesar_skus_desde_scraper(skus):
    """Procesa SKUs desde Scraper con cantidad por defecto = 1"""
    productos = []
    for sku in skus:
        productos.append({
            'sku': sku.strip().upper(),
            'cantidad': 1
        })
    st.session_state.productos_actuales = productos
    st.success(f"✅ Cargados {len(productos)} SKUs desde el Scraper")
    st.rerun()


def mostrar_tabla_productos():
    """Muestra tabla editable de productos"""
    productos = st.session_state.productos_actuales
    
    # Crear DataFrame editable
    df = pd.DataFrame(productos)
    
    # Mostrar tabla con opción de editar cantidades
    st.markdown("**Edita las cantidades directamente en la tabla:**")
    
    # Usar columnas para edición
    for i, prod in enumerate(productos):
        col1, col2, col3 = st.columns([3, 1, 0.5])
        with col1:
            st.markdown(f"`{prod['sku']}`")
        with col2:
            nueva_cant = st.number_input(
                "Cantidad",
                min_value=0,
                value=prod['cantidad'],
                step=1,
                key=f"edit_{i}_{prod['sku']}",
                label_visibility="collapsed"
            )
            if nueva_cant != prod['cantidad']:
                if nueva_cant == 0:
                    st.session_state.productos_actuales.pop(i)
                    st.rerun()
                else:
                    prod['cantidad'] = nueva_cant
        with col3:
            if st.button("🗑️", key=f"del_{i}_{prod['sku']}"):
                st.session_state.productos_actuales.pop(i)
                st.rerun()
    
    # Resumen
    total_productos = len(productos)
    total_unidades = sum(p['cantidad'] for p in productos)
    st.markdown(f"""
    <div style="background:rgba(0,0,0,0.2);border-radius:12px;padding:0.5rem 1rem;margin-top:0.5rem;">
        📦 Total productos: <strong>{total_productos}</strong> | 
        🔢 Total unidades: <strong>{total_unidades}</strong>
    </div>
    """, unsafe_allow_html=True)


def procesar_y_cotizar():
    """Procesa los productos contra stock y genera cotización"""
    productos = st.session_state.productos_actuales
    
    if not productos:
        st.warning("No hay productos para procesar")
        return
    
    # Verificar que haya stock cargado
    if not st.session_state.get('stocks', []):
        st.warning("⚠️ No hay archivos de stock cargados. Usando simulación.")
        usar_simulacion = True
    else:
        usar_simulacion = False
    
    with st.spinner("Procesando productos contra stock..."):
        resultados = []
        
        for prod in productos:
            sku = prod['sku']
            cantidad_solicitada = prod['cantidad']
            
            if usar_simulacion:
                # Simulación de stock
                stock_yessica = 50
                stock_apri004 = 30
                stock_apri001 = 100
                precio = 99.90
                descripcion = f"Producto {sku}"
            else:
                # Aquí irá la búsqueda real en catálogos y stock
                # Por ahora usamos simulación
                stock_yessica = 50
                stock_apri004 = 30
                stock_apri001 = 100
                precio = 99.90
                descripcion = f"Producto {sku}"
            
            # Calcular cantidad cotizable
            cantidad_cotizar, mensaje = calcular_cantidad_total(
                cantidad_solicitada, stock_yessica, stock_apri004, stock_apri001
            )
            
            max_apri = calcular_maximo_apri001(stock_apri001)
            stock_seguro = calcular_stock_seguro(stock_yessica, stock_apri004)
            
            resultados.append({
                'sku': sku,
                'descripcion': descripcion,
                'cantidad_solicitada': cantidad_solicitada,
                'cantidad_cotizar': cantidad_cotizar,
                'precio': precio,
                'total': precio * cantidad_cotizar,
                'estado': mensaje,
                'stock_yessica': stock_yessica,
                'stock_apri004': stock_apri004,
                'stock_apri001': stock_apri001,
                'stock_seguro': stock_seguro,
                'max_apri001': max_apri
            })
        
        st.session_state.resultados_procesados = resultados
        st.success(f"✅ Procesados {len(resultados)} productos")
        st.rerun()


def mostrar_resultados_procesados():
    """Muestra resultados del procesamiento"""
    resultados = st.session_state.resultados_procesados
    
    for r in resultados:
        if r['cantidad_cotizar'] > 0:
            color = "#4CAF50"
            icono = "✅"
        else:
            color = "#f44336"
            icono = "❌"
        
        st.markdown(f"""
        <div style="background:white;border-radius:16px;padding:1rem;margin-bottom:1rem;border-left:5px solid {color};">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <strong style="font-size:1.1rem;">{icono} {r['sku']}</strong>
                    <br>
                    <span style="font-size:0.8rem;color:#666;">{r['descripcion'][:80]}</span>
                </div>
                <div style="text-align:right;">
                    <span style="background:{color};color:white;padding:4px 12px;border-radius:20px;">
                        {r['cantidad_cotizar']}/{r['cantidad_solicitada']}
                    </span>
                </div>
            </div>
            <div style="margin-top:12px;">
                <div style="display:flex;justify-content:space-between;flex-wrap:wrap;">
                    <span>💰 Precio: <strong>S/ {r['precio']:.2f}</strong></span>
                    <span>📦 Stock: Y:{r['stock_yessica']} | A4:{r['stock_apri004']} | A1:{r['stock_apri001']}</span>
                    <span>🔒 Stock seguro: {r['stock_seguro']} | Máx A1: {r['max_apri001']}</span>
                </div>
            </div>
            <div style="margin-top:8px;padding:8px;background:#f5f5f5;border-radius:8px;">
                📌 {r['estado']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Totales
    total_cotizable = sum(r['cantidad_cotizar'] for r in resultados)
    total_valor = sum(r['total'] for r in resultados)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style="background:#4CAF50;border-radius:12px;padding:1rem;text-align:center;">
            <div style="color:white;">📦 TOTAL COTIZABLE</div>
            <div style="color:white;font-size:1.5rem;font-weight:bold;">{total_cotizable} unidades</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background:#2196F3;border-radius:12px;padding:1rem;text-align:center;">
            <div style="color:white;">💰 VALOR TOTAL</div>
            <div style="color:white;font-size:1.5rem;font-weight:bold;">S/ {total_valor:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Botones de acción
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ Agregar al carrito", type="primary", use_container_width=True):
            agregar_resultados_al_carrito()
    
    with col2:
        if st.button("🔄 Reintentar fallidos", use_container_width=True):
            reintentar_fallidos()
    
    with col3:
        if st.button("🗑️ Limpiar resultados", use_container_width=True):
            del st.session_state.resultados_procesados
            st.rerun()


def agregar_resultados_al_carrito():
    """Agrega productos cotizables al carrito global"""
    if 'carrito' not in st.session_state:
        st.session_state.carrito = []
    
    agregados = 0
    for r in st.session_state.resultados_procesados:
        if r['cantidad_cotizar'] > 0:
            # Buscar si ya existe en carrito
            existe = False
            for item in st.session_state.carrito:
                if item['sku'] == r['sku']:
                    item['cantidad'] += r['cantidad_cotizar']
                    item['total'] = item['precio'] * item['cantidad']
                    existe = True
                    break
            
            if not existe:
                st.session_state.carrito.append({
                    'sku': r['sku'],
                    'descripcion': r['descripcion'],
                    'cantidad': r['cantidad_cotizar'],
                    'precio': r['precio'],
                    'total': r['total'],
                    'stock_yessica': r.get('stock_yessica', 0),
                    'stock_apri004': r.get('stock_apri004', 0),
                    'stock_apri001': r.get('stock_apri001', 0)
                })
            agregados += 1
    
    st.success(f"✅ {agregados} productos agregados al carrito")
    st.rerun()


def reintentar_fallidos():
    """Reintenta procesar productos que no pudieron cotizarse"""
    fallidos = [r for r in st.session_state.resultados_procesados if r['cantidad_cotizar'] == 0]
    
    if not fallidos:
        st.info("No hay productos fallidos para reintentar")
        return
    
    # Crear lista para reintentar con cantidad reducida
    productos_reintento = []
    for r in fallidos:
        # Intentar con la mitad de la cantidad
        nueva_cant = max(1, r['cantidad_solicitada'] // 2)
        productos_reintento.append({
            'sku': r['sku'],
            'cantidad': nueva_cant
        })
    
    st.session_state.productos_actuales = productos_reintento
    if 'resultados_procesados' in st.session_state:
        del st.session_state.resultados_procesados
    
    st.info(f"🔄 Reintentando {len(fallidos)} productos con cantidades reducidas")
    st.rerun()


def limpiar_todo():
    """Limpia todas las listas"""
    if 'productos_actuales' in st.session_state:
        st.session_state.productos_actuales = []
    if 'resultados_procesados' in st.session_state:
        del st.session_state.resultados_procesados
    st.success("Todo limpiado correctamente")
    st.rerun()
