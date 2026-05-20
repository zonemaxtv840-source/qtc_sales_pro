# modules/ugreen_handler.py
"""Manejo de búsqueda y procesamiento de productos UGREEN"""

import pandas as pd
from typing import List, Dict, Optional
from utils.excel_utils import corregir_numero


def buscar_ugreen_producto(busqueda: str, ugreen_catalogo: Dict) -> Optional[List[Dict]]:
    """Busca producto en catálogo UGREEN por SKU o descripción"""
    if not ugreen_catalogo:
        return None
    
    df = ugreen_catalogo['df']
    col_sku = ugreen_catalogo['col_sku']
    col_desc = ugreen_catalogo.get('col_desc')
    col_stock = ugreen_catalogo.get('col_stock')
    
    # Búsqueda por SKU o descripción
    mask_sku = df[col_sku].astype(str).str.contains(busqueda, case=False, na=False)
    mask_desc = pd.Series([False] * len(df))
    if col_desc:
        mask_desc = df[col_desc].astype(str).str.contains(busqueda, case=False, na=False)
    
    mask = mask_sku | mask_desc
    coincidencias = df[mask]
    
    if coincidencias.empty:
        return None
    
    resultados = []
    for _, row in coincidencias.iterrows():
        sku = str(row[col_sku]).strip().upper()
        descripcion = str(row[col_desc])[:200] if col_desc else f"SKU: {sku}"
        
        # Extraer precios
        precio_mayor = corregir_numero(row.get('Mayor', 0))
        precio_caja = corregir_numero(row.get('Caja', 0))
        precio_vip = corregir_numero(row.get('Vip', 0))
        precio_pvp = corregir_numero(row.get('PVP', 0))
        
        # Extraer stock
        stock = 0
        if col_stock:
            stock = int(corregir_numero(row[col_stock])) if pd.notna(row[col_stock]) else 0
        
        resultados.append({
            'sku': sku,
            'descripcion': descripcion,
            'precios': {
                'P. IR': precio_mayor,
                'P. BOX': precio_caja,
                'P. VIP': precio_vip,
                'PVP': precio_pvp
            },
            'stock': stock,
            'tiene_stock': stock > 0,
            'tiene_precio': precio_vip > 0 or precio_caja > 0 or precio_mayor > 0,
            'tipo': 'UGREEN'
        })
    
    return resultados
