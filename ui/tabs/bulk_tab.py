# ui/tabs/bulk_tab.py - Placeholder limpio
import streamlit as st

def render_bulk_tab():
    st.markdown("### 📦 MODO MASIVO (Bulk)")
    st.info("🔄 Módulo en construcción... Próximamente: Procesamiento de lista de SKUs")
    st.caption(f"Modo actual: {st.session_state.get('modo', 'XIAOMI')}")
    
    # Sidebar info
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📂 Archivos necesarios")
        st.info("Para usar el modo bulk, carga:\n- Catálogos de precios\n- Reportes de stock")
