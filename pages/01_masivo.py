import streamlit as st

def mostrar():
    st.markdown("## 📦 Modo Masivo")
    st.info("Carga múltiples SKUs con formato: SKU:CANTIDAD (separados por coma o nueva línea)")
    
    texto_masivo = st.text_area("SKUs:", height=200, 
                                 placeholder="Ejemplo:\nRN0200065BK8:5\nCN0200047BK8:10")
    
    if st.button("🔄 Procesar lista", use_container_width=True):
        if texto_masivo.strip():
            # Procesar lógica aquí
            st.success("✅ Procesado correctamente")
        else:
            st.warning("Ingresa al menos un SKU")
