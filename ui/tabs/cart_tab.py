# ui/tabs/cart_tab.py
import streamlit as st

def render_cart_tab():
    st.markdown("### 🛒 CARRITO DE COTIZACIÓN")
    
    if not st.session_state.get('carrito', []):
        st.info("No hay productos en el carrito")
        return
    
    total = 0
    for idx, item in enumerate(st.session_state.carrito):
        col1, col2, col3, col4, col5 = st.columns([2, 3, 1, 1, 0.5])
        with col1:
            st.write(f"**{item['sku']}**")
        with col2:
            st.write(item['descripcion'][:50])
        with col3:
            st.write(item['cantidad'])
        with col4:
            st.write(f"S/ {item['precio']:.2f}")
        with col5:
            if st.button("🗑️", key=f"del_{idx}"):
                st.session_state.carrito.pop(idx)
                st.rerun()
        total += item['total']
    
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#e94560 0%,#c73e54 100%);border-radius:12px;padding:1rem;margin:1rem 0;text-align:center;">
        <span style="color:white;font-size:1.5rem;font-weight:bold;">TOTAL: S/ {total:,.2f}</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🧹 Limpiar carrito", use_container_width=True):
        st.session_state.carrito = []
        st.rerun()
