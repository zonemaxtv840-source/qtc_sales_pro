# ui/tabs/search_tab.py
import streamlit as st

def render_search_tab():
    st.markdown("### 🔍 BÚSQUEDA INTELIGENTE")
    st.info("🔄 Módulo en construcción... Próximamente: Búsqueda por SKU o descripción")
    
    # Búsqueda simple temporal
    busqueda = st.text_input("Buscar producto", placeholder="SKU o descripción")
    
    if busqueda and len(busqueda) >= 3:
        st.write(f"Buscando: {busqueda}")
        st.info("Funcionalidad completa próximamente")
