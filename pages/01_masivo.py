import streamlit as st
from modules.stock_engine import obtener_inventario_completo

def mostrar():
    st.markdown("## 📦 Modo Masivo")
    st.markdown("Carga múltiples SKUs con formato `SKU:CANTIDAD`")
    st.caption("Ejemplo: `RN0200065BK8:5, CN0200047BK8:10` o uno por línea")
    
    texto_masivo = st.text_area("📝 Lista de SKUs:", height=200, 
                                 placeholder="RN0200065BK8:5\nCN0200047BK8:10\nXIAOMI123\nAPRI.004:3")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Procesar lista", use_container_width=True):
            if texto_masivo.strip():
                lineas = texto_masivo.strip().replace(",", "\n").split("\n")
                productos_encontrados = []
                
                for linea in lineas:
                    linea = linea.strip()
                    if not linea:
                        continue
                    
                    if ":" in linea:
                        sku, cant = linea.split(":", 1)
                        try:
                            cantidad = int(cant)
                        except:
                            cantidad = 1
                    else:
                        sku = linea
                        cantidad = 1
                    
                    # Buscar producto
                    inv = obtener_inventario_completo(sku, st.session_state.stock, st.session_state.catalogo)
                    
                    productos_encontrados.append({
                        "sku": inv["sku"],
                        "cantidad": cantidad,
                        "precio": inv["precio"] or 0,
                        "tiene_stock": inv["tiene_stock"]
                    })
                
                # Mostrar resumen
                st.success(f"✅ {len(productos_encontrados)} productos procesados")
                
                # Mostrar tabla de resultados
                import pandas as pd
                df_resultados = pd.DataFrame(productos_encontrados)
                st.dataframe(df_resultados, use_container_width=True)
                
                # Botón para agregar todo al carrito
                if st.button("📦 Agregar todos al carrito"):
                    for p in productos_encontrados:
                        if p["precio"] > 0:
                            st.session_state.carrito.append({
                                "sku": p["sku"],
                                "descripcion": p["sku"],
                                "cantidad": p["cantidad"],
                                "precio": p["precio"]
                            })
                    st.success(f"✅ {len(productos_encontrados)} productos agregados al carrito")
                    st.rerun()
            else:
                st.warning("Ingresa al menos un SKU")
    
    with col2:
        if st.button("🧹 Limpiar", use_container_width=True):
            st.rerun()
