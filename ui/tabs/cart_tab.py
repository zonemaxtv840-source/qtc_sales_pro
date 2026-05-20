# ui/tabs/cart_tab.py - Temporal
import streamlit as st

def render_cart_tab():
    st.markdown("### 🛒 CARRITO DE COTIZACIÓN")
    st.info("🔄 Módulo en construcción... Pronto disponible")
    
    if st.session_state.carrito:
        st.write(f"Productos en carrito: {len(st.session_state.carrito)}")
    else:
        st.info("No hay productos en el carrito")
