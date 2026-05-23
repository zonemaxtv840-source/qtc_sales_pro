# pages/busqueda.py
# TAB 2: BÚSQUEDA INTELIGENTE PROFESIONAL

import streamlit as st
from modules.search_engine import (
    buscar_productos_profesional, 
    autocompletar_busqueda,
    obtener_productos_destacados
)
from modules.ui_components import construir_badge_stock
from utils.helpers import formatear_moneda

def mostrar():
    st.markdown("### 🔍 Búsqueda Inteligente Profesional")
    st.caption("🔎 Búsqueda difusa | Tolerancia a errores | Filtros en tiempo real")
    
    if not st.session_state.catalogos or not st.session_state.stocks:
        st.warning("📌 Carga catálogos y stock en el panel izquierdo")
        return
    
    # Layout de búsqueda
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        query = st.text_input(
            "🔎 Buscar por SKU o descripción", 
            placeholder="Ej: earphones, cargador, RN0200065BK8...",
            key="search_input"
        )
    
    with col2:
        solo_stock = st.checkbox("📦 Solo con stock", value=True)
    
    with col3:
        ordenar = st.selectbox("Ordenar", ["Relevancia", "Precio ↑", "Precio ↓", "Stock ↑"])
    
    # Filtros avanzados
    with st.expander("🔧 Filtros avanzados"):
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            precio_min = st.number_input("Precio mínimo", min_value=0, value=0, step=10)
        with col_f2:
            precio_max = st.number_input("Precio máximo", min_value=0, value=100000, step=100)
        with col_f3:
            solo_precio = st.checkbox("💰 Solo con precio")
    
    # Autocompletado
    if query and len(query) >= 2:
        sugerencias = autocompletar_busqueda(query, st.session_state.catalogos, limite=5)
        if sugerencias:
            st.caption(f"💡 Sugerencias: {', '.join([s['sku'] for s in sugerencias])}")
    
    # Ejecutar búsqueda
    if query and len(query) >= 2:
        with st.spinner("🔍 Buscando..."):
            filtros = {
                "solo_stock": solo_stock,
                "solo_precio": solo_precio,
                "precio_min": precio_min if precio_min > 0 else None,
                "precio_max": precio_max if precio_max < 100000 else None
            }
            resultados = buscar_productos_profesional(
                query, 
                st.session_state.catalogos, 
                st.session_state.stocks, 
                st.session_state.precio_key,
                filtros
            )
            
            if not resultados:
                st.warning(f"No se encontraron resultados para '{query}'")
                return
            
            st.markdown(f"### 📊 {len(resultados)} resultados encontrados")
            
            # Ordenar
            if ordenar == "Precio ↑":
                resultados.sort(key=lambda x: x['precio'] or 999999)
            elif ordenar == "Precio ↓":
                resultados.sort(key=lambda x: x['precio'] or 0, reverse=True)
            elif ordenar == "Stock ↑":
                resultados.sort(key=lambda x: x['stock_total'])
            
            for prod in resultados[:50]:
                badges = construir_badge_stock(prod['stock_yessica'], prod['stock_apri004'], prod['stock_apri001'])
                
                # Color según disponibilidad
                if prod['tiene_stock'] and prod['tiene_precio']:
                    color = "#4CAF50"
                    estado = "✅ Disponible"
                elif prod['tiene_stock'] and not prod['tiene_precio']:
                    color = "#f44336"
                    estado = "⚠️ Stock sin precio"
                elif not prod['tiene_stock'] and prod['tiene_precio']:
                    color = "#2196F3"
                    estado = "📋 Solo precio"
                else:
                    color = "#9e9e9e"
                    estado = "❌ No disponible"
                
                relevancia = f"🎯 {prod['score']:.0f}% match" if prod['score'] > 70 else ""
                
                st.markdown(f"""
                <div style="background:white;border-radius:16px;padding:1rem;margin-bottom:1rem;border-left:5px solid {color};">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div>
                            <strong style="color:#1a1a2e;font-size:1.1rem;">📦 {prod['sku']}</strong>
                            <span style="background:{color};color:white;padding:2px 10px;border-radius:20px;margin-left:10px;">{estado}</span>
                            {f'<span style="background:#ff9800;color:white;padding:2px 10px;border-radius:20px;margin-left:5px;">{relevancia}</span>' if relevancia else ''}
                        </div>
                        <div style="font-size:1.3rem;font-weight:bold;color:#e67e22;">{formatear_moneda(prod['precio'])}</div>
                    </div>
                    <div style="margin-top:10px;color:#555;">
                        <strong>📝 Descripción:</strong> {prod['descripcion']}
                    </div>
                    <div>{badges}</div>
                </div>
                """, unsafe_allow_html=True)
                
                if prod['tiene_stock'] and prod['tiene_precio']:
                    col_cant, col_btn = st.columns([1, 2])
                    with col_cant:
                        cantidad = st.number_input(
                            "Cantidad", min_value=1, max_value=prod['stock_total'], 
                            value=1, key=f"busq_{prod['sku']}", label_visibility="collapsed"
                        )
                    with col_btn:
                        if st.button(f"➕ Agregar a cotización", key=f"add_{prod['sku']}"):
                            st.session_state.carrito.append({
                                'sku': prod['sku'],
                                'descripcion': prod['descripcion'],
                                'cantidad': cantidad,
                                'precio': prod['precio'],
                                'total': prod['precio'] * cantidad,
                                'stock_yessica': prod['stock_yessica'],
                                'stock_apri004': prod['stock_apri004'],
                                'stock_apri001': prod['stock_apri001']
                            })
                            st.success(f"✅ Agregado {cantidad}x {prod['sku']}")
                            st.rerun()
                st.divider()
    
    elif not query:
        # Mostrar productos destacados
        st.markdown("### ⭐ Productos con stock disponible")
        destacados = obtener_productos_destacados(st.session_state.catalogos, st.session_state.stocks, limite=10)
        
        for prod in destacados:
            st.markdown(f"""
            <div style="background:white;border-radius:12px;padding:0.8rem;margin-bottom:0.5rem;">
                <strong style="color:#1a1a2e;">📦 {prod['sku']}</strong><br>
                <span style="color:#555;font-size:0.8rem;">{prod['descripcion'][:80]}</span><br>
                <span style="background:#4CAF50;color:white;padding:2px 8px;border-radius:12px;">Stock: {prod['stock_total']}</span>
            </div>
            """, unsafe_allow_html=True)
