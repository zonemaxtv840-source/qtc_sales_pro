import streamlit as st
from modules.search_engine import BusquedaProfesional
from modules.ui_components import crear_tarjeta_producto
from modules.stock_engine import obtener_inventario_completo

def mostrar():
    st.markdown("## 🔍 Búsqueda Inteligente")
    st.markdown("---")
    
    # Verificar datos en session_state
    if "catalogo" not in st.session_state or "stock" not in st.session_state:
        st.error("Primero carga los archivos en el panel izquierdo")
        return
    
    # Inicializar motor
    motor = BusquedaProfesional(st.session_state.catalogo, st.session_state.stock)
    
    # Filtros y búsqueda en layout profesional
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    
    with col1:
        query = st.text_input("🔎 Buscar por SKU o descripción:", 
                              placeholder="Ej: earphones, cargador, RN0200065BK8...",
                              key="search_input")
    
    with col2:
        solo_stock = st.checkbox("📦 Solo con stock", value=True)
    
    with col3:
        ordenar = st.selectbox("Ordenar", ["Relevancia", "Precio ↑", "Precio ↓"], key="sort_order")
    
    with col4:
        limite = st.selectbox("Mostrar", [10, 20, 50, 100], index=1, key="limit")
    
    # Mostrar productos destacados si no hay búsqueda
    if not query or len(query) < 2:
        st.info("💡 Escribe al menos 2 caracteres para buscar productos")
        
        # Mostrar algunos productos con stock como sugerencia
        st.markdown("### 📌 Productos con stock disponible")
        productos_con_stock = []
        for idx, row in st.session_state.catalogo.head(20).iterrows():
            sku = str(row.get("SKU", ""))
            inv = obtener_inventario_completo(sku, st.session_state.stock, st.session_state.catalogo)
            if inv["tiene_stock"]:
                productos_con_stock.append((row, inv))
        
        for row, inv in productos_con_stock[:5]:
            card = crear_tarjeta_producto(row, inv)
            st.markdown(card, unsafe_allow_html=True)
            
            # Botón para agregar rápido
            col_a, col_b = st.columns([1, 5])
            with col_a:
                cant = st.number_input("Cant.", min_value=1, max_value=inv["stock_total"], 
                                      key=f"suggest_{inv['sku']}", value=1, step=1)
            with col_b:
                if st.button(f"➕ Agregar {inv['sku']}", key=f"suggest_btn_{inv['sku']}"):
                    st.session_state.carrito.append({
                        "sku": inv["sku"],
                        "descripcion": row.get("Descripcion", ""),
                        "cantidad": cant,
                        "precio": inv["precio"] or 0
                    })
                    st.success(f"✅ {cant} x {inv['sku']} agregado")
                    st.rerun()
        return
    
    # Búsqueda activa
    with st.spinner("🔍 Buscando..."):
        filtros = {"solo_stock": solo_stock}
        resultados = motor.buscar(query, filtros)
    
    if not resultados:
        st.warning(f"❌ No se encontraron resultados para '{query}'")
        return
    
    # Ordenar resultados
    if ordenar == "Precio ↑":
        resultados.sort(key=lambda x: x["inventario"]["precio"] or 999999)
    elif ordenar == "Precio ↓":
        resultados.sort(key=lambda x: x["inventario"]["precio"] or 0, reverse=True)
    
    # Mostrar resultados
    st.markdown(f"### 📊 {len(resultados)} resultados encontrados")
    
    for res in resultados[:limite]:
        card = crear_tarjeta_producto(res["row"], res["inventario"])
        st.markdown(card, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 4])
        with col1:
            max_stock = res["inventario"]["stock_total"] or 100
            cantidad = st.number_input("Cantidad:", min_value=1, max_value=max_stock, 
                                       key=f"cant_{res['inventario']['sku']}", value=1, step=1)
        with col2:
            if st.button("➕ Agregar al carrito", key=f"agregar_{res['inventario']['sku']}"):
                st.session_state.carrito.append({
                    "sku": res["inventario"]["sku"],
                    "descripcion": res["row"].get("Descripcion", ""),
                    "cantidad": cantidad,
                    "precio": res["inventario"]["precio"] or 0
                })
                st.success(f"✅ {cantidad} unidad(es) de {res['inventario']['sku']} agregadas")
                st.rerun()
