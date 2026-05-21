# utils/formatters.py
from typing import List, Dict


def construir_badge_stock(stock_yessica: int, stock_apri004: int, stock_apri001: int,
                          detalle_apri001: List[Dict] = None, ubicaciones: List[Dict] = None) -> str:
    """Construye los badges HTML para mostrar stock"""
    badges = []
    
    if stock_yessica > 0:
        badges.append(f'<span class="badge-yessica">🟢 YESSICA: {stock_yessica}</span>')
    if stock_apri004 > 0:
        badges.append(f'<span class="badge-apri004">🟡 APRI.004: {stock_apri004}</span>')
    if stock_apri001 > 0:
        badges.append(f'<span class="badge-apri001">🔴 APRI.001: {stock_apri001} ⚠️</span>')
    
    if not badges:
        return '<span class="badge-warning">❌ Sin stock</span>'
    return ' '.join(badges)


def formatear_precio(precio: float) -> str:
    """Formatea un precio a moneda soles"""
    return f"S/ {precio:,.2f}"
