import streamlit as st
import pandas as pd

def mostrar():
    st.markdown("## 🔧 Analizador de SKUs")
    
    if not st.session_state.get("catalogo") is not None:
        st.warning("Primero carga un catálogo en el sidebar")
        return
    
    df = st.session_state.catalogo
    
    # Estadísticas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total SKUs", len(df))
    with col2:
        skus_norm = df["SKU"].astype(str).str.upper()
        duplicados = skus_norm.duplicated().sum()
        st.metric("SKUs duplicados", duplicados)
    with col3:
        sin_precio = df["Precio VIP"].isna().sum() if "Precio VIP" in df.columns else 0
        st.metric("Sin precio", sin_precio)
    
    # Mostrar duplicados
    if duplicados > 0:
        st.subheader("⚠️ SKUs Duplicados")
        duplicados_df = df[skus_norm.duplicated(keep=False)].sort_values("SKU")
        st.dataframe(duplicados_df, use_container_width=True)
    
    # Detectar SKUs problemáticos
    st.subheader("🔍 SKUs con formato anómalo")
    skus_validos = df["SKU"].astype(str).str.match(r'^[A-Z0-9]{8,}$')
    anomalos = df[~skus_validos]
    if len(anomalos) > 0:
        st.warning(f"{len(anomalos)} SKUs con formato inusual")
        st.dataframe(anomalos[["SKU", "Descripcion"]], use_container_width=True)
