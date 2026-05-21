# modules/stock_logic.py
"""Lógica de manejo de stock para XIAOMI (YESSICA, APRI.004, APRI.001)"""

from typing import List, Dict, Tuple
import pandas as pd
from utils.excel_utils import corregir_numero


def buscar_stock_para_sku(sku: str, stocks: List[Dict]) -> Dict:
    """
    Lee stock según reglas:
    - YESSICA: columna "Disponible" o "Cantidad"
    - APRI.004: columna "Disponible" o "Cantidad"
    - APRI.001: columna "Disponible"
    """
    sku_limpio = sku.strip().upper()
    
    stock_yessica = 0
    stock_apri004 = 0
    stock_apri001 = 0
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
                    stock_apri001 = cantidad
    
    return {
        'yessica': stock_yessica,
        'apri004': stock_apri004,
        'apri001': stock_apri001,
        'total': stock_yessica + stock_apri004 + stock_apri001,
        'ubicaciones': ubicaciones
    }


def calcular_cantidad_total_segura(cantidad_solicitada: int, stock_info: Dict) -> Tuple[int, str, Dict]:
    """
    Calcula la cantidad total a cotizar combinando:
    - Primero: YESSICA + APRI.004 (stock inmediato)
    - Luego: APRI.001 (stock remoto, última opción)
    """
    stock_yessica = stock_info.get('yessica', 0)
    stock_apri004 = stock_info.get('apri004', 0)
    stock_apri001 = stock_info.get('apri001', 0)
    
    stock_inmediato = stock_yessica + stock_apri004
    stock_inmediato_seguro = max(0, stock_inmediato - 2) if stock_inmediato > 0 else 0
    
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
    
    # CASO 2: Necesita APRI.001
    restante = cantidad_solicitada - stock_inmediato_seguro
    
    if stock_apri001 < 20:
        if stock_inmediato_seguro > 0:
            return stock_inmediato_seguro, f"⚠️ Stock inmediato insuficiente. APRI.001: {stock_apri001} < 20", detalle
        else:
            return 0, f"❌ Sin stock disponible (APRI.001: {stock_apri001} < 20)", detalle
    
    if restante < 5:
        if stock_inmediato_seguro > 0:
            return stock_inmediato_seguro, f"⚠️ Pedido restante muy pequeño ({restante} < 5)", detalle
        else:
            return 0, f"❌ Pedido muy pequeño ({restante} < 5)", detalle
    
    max_apri001 = min(int(stock_apri001 * 0.15), 100)
    
    if max_apri001 < 5:
        return stock_inmediato_seguro, f"⚠️ APRI.001: máximo {max_apri001} unidades", detalle
    
    if restante <= max_apri001:
        total_final = stock_inmediato_seguro + restante
        return total_final, f"✅ Stock: {stock_inmediato_seguro} + APRI.001: {restante} = {total_final}", detalle
    else:
        if stock_inmediato_seguro > 0:
            return stock_inmediato_seguro, f"⚠️ APRI.001 no puede cubrir. Máximo: {max_apri001}", detalle
        else:
            return 0, f"❌ No se puede cotizar. Máximo APRI.001: {max_apri001}", detalle


def tiene_stock_inmediato(stock_info: Dict) -> bool:
    """Verifica si hay stock inmediato (YESSICA + APRI.004)"""
    return (stock_info.get('yessica', 0) + stock_info.get('apri004', 0)) > 0


def tiene_solo_apri001(stock_info: Dict) -> bool:
    """Verifica si solo hay stock en APRI.001"""
    return (stock_info.get('apri001', 0) > 0 and 
            stock_info.get('yessica', 0) == 0 and 
            stock_info.get('apri004', 0) == 0)
