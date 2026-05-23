# pages/carrito.py
# TAB 3: CARRITO DE COTIZACIÓN

import streamlit as st
from modules.ui_components import construir_badge_stock
from modules.cart_engine import generar_excel, calcular_total_carrito
from utils.helpers import formatear_moneda
from datetime import datetime

def mostrar():
    st.markdown("### 🛒 Cotización actual")
    
    if not st.session_state.carrito:
        st.info("No hay productos en el carrito")
        return
    
    # Mostrar carrito con descripción COMPLETA
    for idx, item in enumerate(st.session_state.carrito):
        with st.container():
            col1, col2, col3, col4, col5, col6 = st.columns([2, 4, 1, 1, 1, 0.5])
            
            with col1:
                st.markdown(f"**📦 {item['sku']}**")
            
            with col2:
                # Descripción COMPLETA (sin truncar)
                st.markdown(f"<span style='color:#555;'>{item['descripcion']}</span>", unsafe_allow_html=True)
            
            with col3:
                nueva_cant = st.number_input(
                    "Cant", min_value=0, value=item['cantidad'], step=1, 
                    key=f"edit_{idx}", label_visibility="collapsed"
                )
                if nueva_cant != item['cantidad']:
                    if nueva_cant == 0:
                        st.session_state.carrito.pop(idx)
                        st.rerun()
                    else:
                        item['cantidad'] = nueva_cant
                        item['total'] = item['precio'] * nueva_cant
            
            with col4:
                st.markdown(f"<span style='color:#e67e22;'>{formatear_moneda(item['precio'])}</span>", unsafe_allow_html=True)
            
            with col5:
                st.markdown(f"**{formatear_moneda(item['total'])}**")
            
            with col6:
                if st.button("🗑️", key=f"del_{idx}"):
                    st.session_state.carrito.pop(idx)
                    st.rerun()
            
            # Badges de stock
            if item.get('tipo') == 'UGREEN':
                st.markdown(f'<span class="badge-ugreen">📦 UGREEN</span>', unsafe_allow_html=True)
            else:
                badges = construir_badge_stock(
                    item.get('stock_yessica', 0),
                    item.get('stock_apri004', 0),
                    item.get('stock_apri001', 0)
                )
                st.markdown(badges, unsafe_allow_html=True)
            
            st.divider()
    
    # Total general
    total_general = calcular_total_carrito(st.session_state.carrito)
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#e94560 0%,#c73e54 100%);border-radius:12px;padding:1rem;margin:1rem 0;text-align:center;">
        <span style="color:white;font-size:1.5rem;font-weight:bold;">TOTAL: {formatear_moneda(total_general)}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Datos del cliente
    st.markdown("### 📋 Datos del cliente")
    col_cli1, col_cli2 = st.columns(2)
    with col_cli1:
        cliente = st.text_input("Nombre del cliente", placeholder="Ej: Empresa SAC")
    with col_cli2:
        ruc = st.text_input("RUC/DNI", placeholder="Ej: 20123456789")
    
    # Botones de exportación
    col_exp1, col_exp2, col_exp3 = st.columns(3)
    
    with col_exp1:
        if st.button("📥 Exportar Excel", type="primary", use_container_width=True):
            if cliente:
                items_export = [
                    {'sku': i['sku'], 'descripcion': i['descripcion'], 
                     'cantidad': i['cantidad'], 'precio': i['precio'], 'total': i['total']} 
                    for i in st.session_state.carrito
                ]
                excel = generar_excel(items_export, cliente, ruc)
                st.download_button(
                    "💾 Descargar", data=excel, 
                    file_name=f"Cotizacion_{cliente}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", 
                    use_container_width=True
                )
                st.balloons()
                st.success("✅ Cotización generada")
            else:
                st.warning("Ingresa el nombre del cliente")
    
    with col_exp2:
        if st.button("📋 Copiar CSV", use_container_width=True):
            csv_text = "SKU,Descripción,Cantidad,Precio,Subtotal\n"
            for item in st.session_state.carrito:
                csv_text += f"{item['sku']},{item['descripcion']},{item['cantidad']},{item['precio']:.2f},{item['total']:.2f}\n"
            csv_text += f"TOTAL,{total_general:.2f}"
            st.code(csv_text, language="csv")
    
    with col_exp3:
        if st.button("🧹 Limpiar todo", use_container_width=True):
            st.session_state.carrito = []
            st.rerun()
