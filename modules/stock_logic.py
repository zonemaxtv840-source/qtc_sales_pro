# modules/stock_logic.py
"""Lógica de manejo de stock para XIAOMI (YESSICA, APRI.004, APRI.001)"""

from typing import List, Dict, Tuple
import pandas as pd
from utils.excel_utils import corregir_numero, detectar_columna_sku
from config.rules import APRI001_RULES, STOCK_SEGURITY_MARGIN


def buscar_stock_para_sku(sku: str, stocks: List[Dict]) -> Dict:
    """
    Lee stock según reglas:
    - YESSICA: columna "Disponible" o "Cantidad"
    - APRI.004: columna "Disponible" o "Cantidad"
    - APRI.001: SOLO columna "Disponible"
    - NO duplica: cada hoja aporta una sola vez
    """
    sku_limpio = sku.strip().upper()
    
    stock_yessica = 0
    stock_apri004 = 0
    stock_apri001 = 0
    detalle_apri001 = []
    ubicaciones = []
    
    for stock in stocks:
        df = stock['df']
        hoja_nombre = stock['hoja']
        df_sku = df[stock['col_sku']].astype(str).str.strip().str.upper()
        mask = df_sku == sku_limpio
        
        if mask.any():
            # Buscar columna de cantidad/disponible
            col_cant = None
            for col in df.columns:
                col_upper = str(col).upper()
                if any(p in col_upper for p in ['CANT', 'STOCK', 'DISPONIBLE', 'UNIDADES']):
                    col_cant = col
                    break
            
            if col_cant:
                row = df[mask].iloc[0]
                cantidad = int(corregir_numero(row[col_cant]))
                col_nombre = str(col_cant).upper()
                hoja_upper = hoja_nombre.upper()
                
                ubicaciones.append({
                    'hoja': hoja_nombre,
                    'columna': col_cant,
                    'cantidad': cantidad
                })
                
                if 'YESSICA' in hoja_upper:
                    stock_yessica = cantidad
                elif 'APRI.004' in hoja_upper:
                    stock_apri004 = cantidad
                elif 'APRI.001' in hoja_upper:
                    if 'DISPONIBLE' in col_nombre:
                        stock_apri001 = cantidad
                        detalle = {'cantidad': cantidad, 'hoja': hoja_nombre}
                        for col in df.columns:
                            col_upper = str(col).upper()
                            if 'OBS' in col_upper or 'DETALLE' in col_upper or 'NOTA' in col_upper:
                                detalle['observacion'] = str(row[col])[:150]
                                break
                        detalle_apri001.append(detalle)
    
    return {
        'yessica': stock_yessica,
        'apri004': stock_apri004,
        'apri001': stock_apri001,
        'detalle_apri001': detalle_apri001,
        'total': stock_yessica + stock_apri004 + stock_apri001,
        'ubicaciones': ubicaciones
    }


def calcular_cantidad_total_segura(cantidad_solicitada: int, stock_info: Dict) -> Tuple[int, str, Dict]:
    """
    Calcula la cantidad total a cotizar combinando:
    - Primero: YESSICA + APRI.004 (stock inmediato, regla stock - STOCK_SEGURITY_MARGIN)
    - Luego: APRI.001 (si falta, con regla de porcentaje)
    """
    
    stock_yessica = stock_info.get('yessica', 0)
    stock_apri004 = stock_info.get('apri004', 0)
    stock_apri001 = stock_info.get('apri001', 0)
    
    stock_inmediato = stock_yessica + stock_apri004
    stock_inmediato_seguro = max(0, stock_inmediato - STOCK_SEGURITY_MARGIN) if stock_inmediato > 0 else 0
    
    detalle = {
        'yessica': stock_yessica,
        'apri004': stock_apri004,
        'apri001': stock_apri001,
        'stock_inmediato': stock_inmediato,
        'stock_inmediato_seguro': stock_inmediato_seguro
    }
    
    # CASO 1: Stock inmediato suficiente
    if cantidad_solicitada <= stock_inmediato_seguro:
        return cantidad_solicitada, f"✅ OK - Stock inmediato: {cantidad_solicitada} unidades", detalle
    
    # CASO 2: Stock inmediato insuficiente
    restante = cantidad_solicitada - stock_inmediato_seguro
    
    # Verificar stock mínimo APRI.001
    if stock_apri001 < APRI001_RULES["stock_minimo"]:
        if stock_inmediato_seguro > 0:
            return stock_inmediato_seguro, f"⚠️ Stock inmediato insuficiente. APRI.001: {stock_apri001} < {APRI001_RULES['stock_minimo']}", detalle
        else:
            return 0, f"❌ Sin stock disponible (APRI.001: {stock_apri001} < {APRI001_RULES['stock_minimo']})", detalle
    
    # Verificar pedido mínimo
    if restante < APRI001_RULES["pedido_minimo"]:
        if stock_inmediato_seguro > 0:
            return stock_inmediato_seguro, f"⚠️ Pedido restante muy pequeño ({restante} < {APRI001_RULES['pedido_minimo']})", detalle
        else:
            return 0, f"❌ Pedido muy pequeño ({restante} < {APRI001_RULES['pedido_minimo']})", detalle
    
    # Calcular máximo permitido de APRI.001
    max_apri001 = min(int(stock_apri001 * APRI001_RULES["porcentaje_maximo"]), APRI001_RULES["tope_maximo"])
    
    if max_apri001 < APRI001_RULES["pedido_minimo"]:
        return stock_inmediato_seguro, f"⚠️ APRI.001: máximo {max_apri001} unidades (<{APRI001_RULES['pedido_minimo']})", detalle
    
    if restante <= max_apri001:
        total_final = stock_inmediato_seguro + restante
        return total_final, f"✅ Stock: {stock_inmediato_seguro} + APRI.001: {restante} = {total_final}", detalle
    else:
        if stock_inmediato_seguro > 0:
            return stock_inmediato_seguro, f"⚠️ APRI.001 no puede cubrir. Máximo: {max_apri001}", detalle
        else:
            return 0, f"❌ No se puede cotizar. Máximo APRI.001: {max_apri001}", detalle


def calcular_cantidad_apri001_only(cantidad_solicitada: int, stock_apri001: int) -> Tuple[int, str, Dict]:
    """Calcula cantidad cotizable cuando SOLO hay stock en APRI.001"""
    
    detalle = {'stock_apri001': stock_apri001}
    
    if stock_apri001 < APRI001_RULES["stock_minimo"]:
        return 0, f"❌ Stock APRI.001 insuficiente ({stock_apri001} < {APRI001_RULES['stock_minimo']})", detalle
    
    if cantidad_solicitada < APRI001_RULES["pedido_minimo"]:
        return 0, f"❌ Pedido muy pequeño ({cantidad_solicitada} < {APRI001_RULES['pedido_minimo']})", detalle
    
    max_apri001 = min(int(stock_apri001 * APRI001_RULES["porcentaje_maximo"]), APRI001_RULES["tope_maximo"])
    
    if max_apri001 < APRI001_RULES["pedido_minimo"]:
        return 0, f"❌ Stock APRI.001 muy bajo. 15% = {max_apri001} unidades", detalle
    
    if cantidad_solicitada > max_apri001:
        return 0, f"❌ Pedido excede límite. Máximo: {max_apri001} unidades", detalle
    
    return cantidad_solicitada, f"✅ OK - APRI.001: {cantidad_solicitada}/{max_apri001} unidades", detalle


def tiene_stock_inmediato(stock_info: Dict) -> bool:
    """Verifica si hay stock inmediato (YESSICA + APRI.004)"""
    return (stock_info.get('yessica', 0) + stock_info.get('apri004', 0)) > 0


def tiene_solo_apri001(stock_info: Dict) -> bool:
    """Verifica si solo hay stock en APRI.001"""
    return (stock_info.get('apri001', 0) > 0 and 
            stock_info.get('yessica', 0) == 0 and 
            stock_info.get('apri004', 0) == 0)
