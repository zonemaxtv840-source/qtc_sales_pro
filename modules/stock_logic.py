# modules/stock_logic.py
"""Lógica de stock para XIAOMI"""

def calcular_stock_seguro(stock_yessica: int, stock_apri004: int) -> int:
    """Calcula stock seguro de YESSICA + APRI.004"""
    stock_inmediato = stock_yessica + stock_apri004
    return max(0, stock_inmediato - 2) if stock_inmediato > 0 else 0


def calcular_maximo_apri001(stock_apri001: int) -> int:
    """Calcula máximo permitido de APRI.001 (15%, tope 100)"""
    if stock_apri001 < 20:
        return 0
    maximo = int(stock_apri001 * 0.15)
    return min(maximo, 100)


def calcular_cantidad_total(cantidad_solicitada: int, 
                            stock_yessica: int, 
                            stock_apri004: int, 
                            stock_apri001: int) -> tuple:
    """
    Calcula cantidad cotizable según reglas
    Retorna: (cantidad_cotizable, mensaje)
    """
    stock_seguro = calcular_stock_seguro(stock_yessica, stock_apri004)
    max_apri001 = calcular_maximo_apri001(stock_apri001)
    
    # Caso: stock inmediato suficiente
    if cantidad_solicitada <= stock_seguro:
        return cantidad_solicitada, f"✅ OK - Stock inmediato: {cantidad_solicitada}"
    
    # Caso: necesita APRI.001
    restante = cantidad_solicitada - stock_seguro
    
    if max_apri001 == 0:
        if stock_seguro > 0:
            return stock_seguro, f"⚠️ Solo stock inmediato: {stock_seguro} (APRI.001 no disponible)"
        return 0, "❌ Sin stock disponible"
    
    if restante <= max_apri001:
        total = stock_seguro + restante
        return total, f"✅ Stock: {stock_seguro} + APRI.001: {restante} = {total}"
    else:
        if stock_seguro > 0:
            return stock_seguro, f"⚠️ APRI.001 máximo: {max_apri001}. Solo stock inmediato: {stock_seguro}"
        return 0, f"❌ Máximo APRI.001: {max_apri001}, necesitas {restante}"
