import streamlit as st
from modules.search_engine import BusquedaProfesional
from modules.ui_components import crear_tarjeta_producto

def mostrar():
    st.markdown("## 🔍 Búsqueda Inteligente")
    
    # Inicializar motor si hay datos
    if st.session_state.get("catalogo") and st.session_state.get("stock"):
        motor = BusquedaProfesional(st.session_state.catalogo, st.session_state.stock)
        
        # Campo de búsqueda
        col1, col2, col3 = st.columns([3,1,1])
        with col1:
            query = st.text_input("🔎 Buscar por SKU o descripción:", 
                                  placeholder="Ej: earphones, RN0200065BK8...")
        
        with col2:
            solo_stock = st.checkbox("📦 Solo con stock")
        
        with col3:
            ordenar = st.selectbox("Ordenar", ["Relevancia", "Precio menor", "Precio mayor"])
        
        # Búsqueda automática
        if query and len(query) >= 2:
            filtros = {"solo_stock": solo_stock}
            resultados = motor.buscar(query, filtros)
            
            st.markdown(f"### 📊 {len(resultados)} resultados encontrados")
            
            for res in resultados[:20]:  # Paginación básica
                card = crear_tarjeta_producto(res["row"], res["inventario"])
                st.markdown(card, unsafe_allow_html=True)
                
                col1, col2 = st.columns([1,4])
                with col1:
                    cantidad = st.number_input("Cantidad:", min_value=1, max_value=1000, 
                                               key=f"cant_{res['inventario']['sku']}")
                with col2:
                    if st.button("➕ Agregar", key=f"agregar_{res['inventario']['sku']}"):
                        st.session_state.carrito.append({
                            "sku": res["inventario"]["sku"],
                            "descripcion": res["row"].get("Descripcion", ""),
                            "cantidad": cantidad,
                            "precio": res["inventario"]["precio"]
                        })
                        st.success(f"✅ {cantidad} unidades agregadas")
