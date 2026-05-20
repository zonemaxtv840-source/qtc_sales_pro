# ui/components.py
"""Componentes reutilizables de UI"""

import streamlit as st
from datetime import datetime
from typing import Dict, List
from utils.formatters import construir_badge_stock, formatear_precio


def mostrar_tarjeta_producto(prod: Dict, modo: str = "XIAOMI"):
    """Muestra una tarjeta de producto en los resultados de búsqueda"""
    
    if modo == "UGREEN" or prod.get('tipo') == 'UGREEN':
        stock_seguro = max(0, prod.get('stock_total', 0) - 2)
        badge = f'<span class="badge-ugreen">📦 UGREEN: {prod.get("stock_total", 0)} (seguro: {stock_seguro})</span>'
        
        st.markdown(f"""
        <div style="background:white;border-radius:16px;padding:1rem;margin-bottom:1rem;border-left:5px solid #00BCD4;color:#1a1a2e;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div><strong style="color:#1a1a2e;">📦 {prod['sku']}</strong> <span style="background:#00BCD4;color:white;padding:2px 8px;border-radius:12px;font-size:0.7rem;">UGREEN</span></div>
            </div>
            <div style="margin-top:8px;"><span style="font-size:0.85rem;color:#1a1a2e;">{prod.get('descripcion', '')[:100]}</span></div>
            <div style="margin-top:8px;color:#1a1a2e;">💰 Precio: <strong>{formatear_precio(prod.get('precio', 0))}</strong></div>
            <div style="margin-top:8px;">{badge}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        badge = construir_badge_stock(
            prod.get('stock_yessica', 0),
            prod.get('stock_apri004', 0),
            prod.get('stock_apri001', 0),
            prod.get('detalle_apri001', []),
            prod.get('ubicaciones', [])
        )
        
        st.markdown(f"""
        <div style="background:white;border-radius:16px;padding:1rem;margin-bottom:1rem;border-left:5px solid #4CAF50;color:#1a1a2e;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div><strong style="font-size:1rem;">📦 {prod['sku']}</strong></div>
            </div>
            <div style="margin-top:12px;"><strong>📝 Descripción:</strong> {prod.get('descripcion', '')}</div>
            <div style="margin-top:8px;"><strong>💰 Precio:</strong> <span style="font-weight:bold;">{formatear_precio(prod.get('precio', 0))}</span></div>
            <div style="margin-top:8px;">{badge}</div>
        </div>
        """, unsafe_allow_html=True)


def mostrar_resumen_bulk(resultados: List[Dict]):
    """Muestra resumen de procesamiento masivo"""
    total_ingresados = len(resultados)
    total_encontrados = sum(1 for p in resultados if p.get('tiene_precio', False))
    total_con_stock = sum(1 for p in resultados if p.get('tiene_stock', False))
    total_sin_precio = total_ingresados - total_encontrados
    total_sin_stock = total_ingresados - total_con_stock
    
    st.markdown(f"""
    <div style="background:rgba(0,0,0,0.3);border-radius:12px;padding:1rem;margin-bottom:1rem;">
        <div style="display:flex;justify-content:space-around;flex-wrap:wrap;">
            <div><span>📋 Ingresados:</span> <strong>{total_ingresados}</strong></div>
            <div style="color:#4CAF50;"><span>✅ Con precio:</span> <strong>{total_encontrados}</strong></div>
            <div><span>📦 Con stock:</span> <strong>{total_con_stock}</strong></div>
            <div style="color:#f44336;"><span>❌ Sin precio:</span> <strong>{total_sin_precio}</strong></div>
            <div style="color:#f44336;"><span>🚫 Sin stock:</span> <strong>{total_sin_stock}</strong></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def mostrar_header(user_name: str, user_role: str):
    """Muestra el header de la aplicación"""
    col1, col2, col3 = st.columns([1, 5, 2])
    
    with col1:
        try:
            st.image("logo.png", width=60)
        except:
            st.markdown("**QTC**", unsafe_allow_html=True)
    
    with col2:
        st.markdown("# QTC Smart Sales Pro")
        st.caption("Sistema Profesional de Cotización | Soporte XIAOMI · UGREEN · OTRAS MARCAS")
    
    with col3:
        role_badge = {"ADMIN": "🔧", "KAM": "⭐", "VENDEDOR": "🛒", "INVITADO": "👤"}
        badge = role_badge.get(user_role, "👤")
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.1); padding: 0.5rem 1rem; border-radius: 12px; text-align: right;">
            <span>{badge} {user_name}</span><br>
            <span style="font-size: 0.7rem;">{user_role}</span>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 Cerrar Sesión", key="logout"):
            return False
    return True
