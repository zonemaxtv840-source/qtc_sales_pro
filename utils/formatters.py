# utils/formatters.py
"""Funciones para formatear y mostrar datos visualmente"""

import streamlit as st
from typing import List, Dict


def construir_badge_stock(stock_yessica: int, stock_apri004: int, stock_apri001: int, 
                          detalle_apri001: List[Dict] = None, ubicaciones: List[Dict] = None) -> str:
    """Construye los badges HTML para mostrar stock"""
    badges = []
    
    if ubicaciones:
        for ub in ubicaciones:
            hoja = ub.get('hoja', '')
            cantidad = ub.get('cantidad', 0)
            if 'YESSICA' in hoja.upper():
                badges.append(f'<span class="badge-yessica">🟢 YESSICA: {cantidad}</span>')
            elif 'APRI.004' in hoja.upper():
                badges.append(f'<span class="badge-apri004">🟡 APRI.004: {cantidad}</span>')
            elif 'APRI.001' in hoja.upper():
                badge_text = f'🔴 APRI.001: {cantidad} (Disponible)'
                if detalle_apri001 and len(detalle_apri001) > 0:
                    for det in detalle_apri001:
                        if det.get('observacion'):
                            badge_text += f' | 📝 {det["observacion"][:50]}'
                            break
                badges.append(f'<span class="badge-apri001">{badge_text} ⚠️</span>')
    else:
        if stock_yessica > 0:
            badges.append(f'<span class="badge-yessica">🟢 YESSICA: {stock_yessica}</span>')
        if stock_apri004 > 0:
            badges.append(f'<span class="badge-apri004">🟡 APRI.004: {stock_apri004}</span>')
        if stock_apri001 > 0:
            badge_text = f'🔴 APRI.001: {stock_apri001} (Disponible)'
            if detalle_apri001 and len(detalle_apri001) > 0:
                for det in detalle_apri001:
                    if det.get('observacion'):
                        badge_text += f' | 📝 {det["observacion"][:50]}'
                        break
            badges.append(f'<span class="badge-apri001">{badge_text} ⚠️</span>')
    
    if not badges:
        return '<span class="badge-warning">❌ Sin stock</span>'
    return ' '.join(badges)


def formatear_precio(precio: float) -> str:
    """Formatea un precio a moneda soles"""
    return f"S/ {precio:,.2f}"


def formatear_total(total: float) -> str:
    """Formatea un total a moneda soles"""
    return f"S/ {total:,.2f}"
