# ui/tabs/cart_tab.py
import streamlit as st

def render_cart_tab():
    st.markdown("### 🛒 CARRITO DE COTIZACIÓN")
    
    if st.session_state.get('carrito', []):
        st.write(f"Productos en carrito: {len(st.session_state.carrito)}")
        for item in st.session_state.carrito:
            st.write(f"- {item.get('sku')}: {item.get('cantidad')} x S/ {item.get('precio', 0):.2f}")
    else:
        st.info("No hay productos en el carrito")
