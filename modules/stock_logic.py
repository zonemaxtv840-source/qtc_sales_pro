# modules/stock_logic.py
from typing import List, Dict, Tuple
from utils.excel_utils import corregir_numero


def buscar_stock_para_sku(sku: str, stocks: List[Dict]) -> Dict:
    """Busca stock de un SKU en todas las hojas"""
    sku_limpio = sku.strip().upper()
    stock_yessica = 0
    stock_apri004 = 0
    stock_apri001 = 0
    
    for stock in stocks:
        df = stock['df']
        hoja = stock.get('hoja', '')
        df_sku = df[stock['col_sku']].astype(str).str.strip().str.upper()
        mask = df_sku == sku_limpio
        
        if mask.any():
            # Buscar columna de cantidad
            col_cant = None
            for col in df.columns:
                col_upper = str(col).upper()
                if any(p in col_upper for p in ['CANT', 'STOCK', 'DISPONIBLE', 'UNIDADES']):
                    col_cant = col
                    break
            
            if col_cant:
                row = df[mask].iloc[0]
                cantidad = int(corregir_numero(row[col_cant]))
                hoja_upper = hoja.upper()
                
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
        'total': stock_yessica + stock_apri004 + stock_apri001
    }


def calcular_cantidad_total_segura(cantidad_solicitada: int, stock_info: Dict) -> Tuple[int, str, Dict]:
    """
    Calcula la cantidad total a cotizar
    stock_info: dict con keys 'yessica', 'apri004', 'apri001'
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
    
    # Stock inmediato suficiente
    if cantidad_solicitada <= stock_inmediato_seguro:
        return cantidad_solicitada, f"✅ OK - Stock inmediato: {cantidad_solicitada}", detelle
    
    # Necesita APRI.001
    restante = cantidad_solicitada - stock_inmediato_seguro
    
    # Reglas APRI.001
    if stock_apri001 < 20:
        if stock_inmediato_seguro > 0:
            return stock_inmediato_seguro, f"⚠️ Stock inmediato: {stock_inmediato_seguro} (APRI.001: {stock_apri001} < 20)", detalle
        return 0, f"❌ Sin stock (APRI.001: {stock_apri001} < 20)", detalle
    
    if restante < 5:
        if stock_inmediato_seguro > 0:
            return stock_inmediato_seguro, f"⚠️ Pedido restante muy pequeño ({restante} < 5)", detalle
        return 0, f"❌ Pedido muy pequeño ({restante} < 5)", detalle
    
    max_apri001 = min(int(stock_apri001 * 0.15), 100)
    
    if max_apri001 < 5:
        return stock_inmediato_seguro, f"⚠️ APRI.001 máximo: {max_apri001} unidades", detalle
    
    if restante <= max_apri001:
        total = stock_inmediato_seguro + restante
        return total, f"✅ Stock: {stock_inmediato_seguro} + APRI.001: {restante} = {total}", detalle
    else:
        if stock_inmediato_seguro > 0:
            return stock_inmediato_seguro, f"⚠️ APRI.001 máximo: {max_apri001}. Solo stock inmediato: {stock_inmediato_seguro}", detalle
        return 0, f"❌ Máximo APRI.001: {max_apri001}, necesita {restante}", detalle
