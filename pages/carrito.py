import streamlit as st
import pandas as pd

def mostrar():
    st.markdown("## 🛒 Carrito de Cotización")
    
    if not st.session_state.carrito:
        st.info("El carrito está vacío. Agrega productos desde MODO MASIVO o BÚSQUEDA.")
        return
    
    # Mostrar carrito
    total = 0
    for i, item in enumerate(st.session_state.carrito):
        subtotal = item["cantidad"] * item["precio"]
        total += subtotal
        
        col1, col2, col3, col4, col5 = st.columns([2,3,1,1,1])
        with col1:
            st.write(item["sku"])
        with col2:
            st.write(item["descripcion"][:40])
        with col3:
            st.write(f"S/ {item['precio']:.2f}")
        with col4:
            st.write(item["cantidad"])
        with col5:
            st.write(f"S/ {subtotal:.2f}")
        
        if st.button("❌", key=f"del_{i}"):
            st.session_state.carrito.pop(i)
            st.rerun()
    
    st.divider()
    col1, col2, col3 = st.columns([2,1,1])
    with col2:
        st.metric("TOTAL", f"S/ {total:.2f}")
    with col3:
        if st.button("📥 Exportar a Excel", use_container_width=True):
            df = pd.DataFrame(st.session_state.carrito)
            df.to_excel("cotizacion.xlsx", index=False)
            st.success("✅ Cotización exportada")
        if st.button("🗑️ Limpiar carrito", use_container_width=True):
            st.session_state.carrito = []
            st.rerun()
