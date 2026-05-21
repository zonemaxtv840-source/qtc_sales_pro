# ui/tabs/bulk_tab.py
import streamlit as st
from modules.stock_logic import calcular_cantidad_total, calcular_maximo_apri001


def render_bulk_tab():
    st.markdown("### 📦 MODO MASIVO (Bulk)")
    st.caption("Formato: `SKU:CANTIDAD` (uno por línea)")
    
    texto_bulk = st.text_area(
        "",
        height=200,
        placeholder="Ejemplo:\nRN9401276NA8:100\nCN0200047BK8:50"
    )
    
    if st.button("🚀 Procesar lista", type="primary", use_container_width=True):
        if not texto_bulk:
            st.warning("Ingresa productos")
        else:
            procesar_lista(texto_bulk)
    
    # Mostrar resultados
    if 'resultados_bulk' in st.session_state:
        mostrar_resultados()


def procesar_lista(texto_bulk):
    """Procesa lista de SKUs (versión de prueba)"""
    pedidos = []
    for line in texto_bulk.strip().split('\n'):
        if ':' in line:
            parts = line.split(':')
            if len(parts) == 2:
                try:
                    sku = parts[0].strip().upper()
                    cant = int(parts[1].strip())
                    if cant > 0:
                        pedidos.append({'sku': sku, 'cantidad': cant})
                except:
                    pass
    
    if not pedidos:
        st.warning("No hay productos válidos")
        return
    
    # SIMULACIÓN de stock (mientras no tengas archivos)
    resultados = []
    for p in pedidos:
        # Simular stock (después conectarás con tus Excel)
        stock_yessica = 50
        stock_apri004 = 30
        stock_apri001 = 100
        
        cantidad, mensaje = calcular_cantidad_total(
            p['cantidad'], stock_yessica, stock_apri004, stock_apri001
        )
        max_apri = calcular_maximo_apri001(stock_apri001)
        
        resultados.append({
            'sku': p['sku'],
            'cantidad_solicitada': p['cantidad'],
            'cantidad_cotizar': cantidad,
            'estado': mensaje,
            'stock_info': f"Y:{stock_yessica} A4:{stock_apri004} A1:{stock_apri001} (max A1:{max_apri})"
        })
    
    st.session_state.resultados_bulk = resultados
    st.success(f"✅ Procesados {len(pedidos)} productos")


def mostrar_resultados():
    """Muestra resultados del procesamiento"""
    st.markdown("---")
    st.markdown("### 📋 Resultados")
    
    for r in st.session_state.resultados_bulk:
        color = "✅" if r['cantidad_cotizar'] > 0 else "❌"
        st.markdown(f"""
        <div style="background:white;border-radius:16px;padding:1rem;margin-bottom:1rem;">
            <strong>📦 {r['sku']}</strong><br>
            Solicitado: {r['cantidad_solicitada']} → Cotizable: <strong>{r['cantidad_cotizar']}</strong><br>
            📌 {r['estado']}<br>
            <span style="font-size:0.7rem;">{r['stock_info']}</span>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("🗑️ Limpiar resultados"):
        del st.session_state.resultados_bulk
        st.rerun()
