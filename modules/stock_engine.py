# modules/stock_engine.py
# Lógica de stock, búsqueda de productos y SKU equivalente

import pandas as pd
from typing import List, Dict, Optional
from difflib import SequenceMatcher
from utils.helpers import corregir_numero, normalizar_texto

def buscar_stock_para_sku(sku: str, stocks: List[Dict]) -> Dict:
    """
    Busca stock - CADA ALMACÉN POR SEPARADO (NO SUMA)
    SOLO usa la columna "Disponible" o "Cantidad"
    """
    sku_limpio = sku.strip().upper()
    stock_yessica = 0
    stock_apri004 = 0
    stock_apri001 = 0
    
    for stock in stocks:
        df = stock['df']
        df_sku = df[stock['col_sku']].astype(str).str.strip().str.upper()
        mask = df_sku == sku_limpio
        if mask.any():
            row = df[mask].iloc[0]
            col_cant = stock.get('col_cant')
            
            if col_cant:
                cantidad = int(corregir_numero(row[col_cant]))
                hoja = stock['hoja'].upper()
                
                # ASIGNAR, NO SUMAR
                if 'YESSICA' in hoja:
                    stock_yessica = cantidad
                elif 'APRI.004' in hoja:
                    stock_apri004 = cantidad
                elif 'APRI.001' in hoja:
                    stock_apri001 = cantidad
    
    return {
        'yessica': stock_yessica,
        'apri004': stock_apri004,
        'apri001': stock_apri001,
        'total': stock_yessica + stock_apri004 + stock_apri001
    }

def calcular_similitud(texto1: str, texto2: str) -> float:
    """Calcula similitud entre dos textos"""
    if not texto1 or not texto2:
        return 0.0
    
    texto1 = normalizar_texto(texto1)
    texto2 = normalizar_texto(texto2)
    
    if texto1 == texto2:
        return 100.0
    
    palabras1 = set(texto1.split())
    palabras2 = set(texto2.split())
    
    interseccion = len(palabras1.intersection(palabras2))
    union = len(palabras1.union(palabras2))
    
    if union == 0:
        return 0.0
    
    jaccard = interseccion / union
    sequence_match = SequenceMatcher(None, texto1, texto2).ratio()
    
    similitud = (jaccard * 0.6 + sequence_match * 0.4) * 100
    return round(similitud, 1)

def buscar_sku_por_descripcion(descripcion: str, catalogos: List[Dict], precio_key: str, umbral: float = 70.0) -> Optional[Dict]:
    """Busca un SKU en catálogos por descripción similar"""
    if not descripcion or not catalogos:
        return None
    
    desc_norm = normalizar_texto(descripcion)
    mejores_matches = []
    
    for cat in catalogos:
        df = cat['df']
        col_desc = cat.get('col_desc')
        if not col_desc:
            continue
        
        if precio_key not in cat.get('precios', {}):
            continue
        
        col_precio = cat['precios'][precio_key]
        
        for _, row in df.iterrows():
            desc_cat = normalizar_texto(str(row[col_desc]))
            similitud = calcular_similitud(desc_norm, desc_cat)
            
            if similitud >= umbral:
                try:
                    precio = float(row[col_precio]) if pd.notna(row[col_precio]) else 0
                    if precio > 0:
                        mejores_matches.append({
                            'precio': precio,
                            'sku_match': str(row[cat['col_sku']]).strip(),
                            'similitud': similitud,
                            'catalogo': cat['nombre'][:30]
                        })
                except:
                    pass
    
    if mejores_matches:
        mejores_matches.sort(key=lambda x: x['similitud'], reverse=True)
        return mejores_matches[0]
    
    return None

def buscar_producto(sku: str, catalogos: List[Dict], stocks: List[Dict], precio_key: str) -> Dict:
    """Busca producto completo (stock + precio + descripción + SKU equivalente)"""
    sku_limpio = sku.strip().upper()
    
    # PASO 1: BUSCAR STOCK
    stock_info = buscar_stock_para_sku(sku_limpio, stocks)
    
    # PASO 2: BUSCAR DESCRIPCIÓN Y PRECIO
    descripcion = f"SKU: {sku}"
    precio = 0.0
    sku_equivalente = None
    similitud_equivalente = 0
    precio_equivalente = 0
    
    for cat in catalogos:
        df = cat['df']
        df_sku = df[cat['col_sku']].astype(str).str.strip().str.upper()
        mask = df_sku == sku_limpio
        if mask.any():
            row = df[mask].iloc[0]
            if precio_key in cat['precios']:
                col_precio = cat['precios'][precio_key]
                precio = corregir_numero(row[col_precio])
            if cat['col_desc']:
                descripcion = str(row[cat['col_desc']])[:200]
            break
    
    stock_total = stock_info['total']
    
    # Si no encontró descripción pero tiene stock, buscarla en STOCK
    if descripcion == f"SKU: {sku}" and stock_total > 0:
        for stock in stocks:
            df = stock['df']
            df_sku = df[stock['col_sku']].astype(str).str.strip().str.upper()
            mask = df_sku == sku_limpio
            if mask.any():
                row = df[mask].iloc[0]
                for col in df.columns:
                    col_upper = str(col).upper()
                    if any(p in col_upper for p in ['DESC', 'DESCRIPCION', 'PRODUCTO', 'NOMBRE']):
                        desc_stock = str(row[col])[:200]
                        if desc_stock and desc_stock != 'nan':
                            descripcion = desc_stock
                            break
                break
    
    # PASO 3: SI TIENE STOCK PERO NO PRECIO → BUSCAR POR DESCRIPCIÓN
    if precio == 0 and stock_total > 0 and descripcion and descripcion != f"SKU: {sku}":
        match = buscar_sku_por_descripcion(descripcion, catalogos, precio_key, umbral=70.0)
        
        if match and match['precio'] > 0:
            sku_equivalente = match['sku_match']
            similitud_equivalente = match['similitud']
            precio_equivalente = match['precio']
    
    return {
        'sku': sku,
        'descripcion': descripcion,
        'precio': precio,
        'precio_equivalente': precio_equivalente,
        'stock_yessica': stock_info['yessica'],
        'stock_apri004': stock_info['apri004'],
        'stock_apri001': stock_info['apri001'],
        'stock_total': stock_total,
        'tiene_stock': stock_total > 0,
        'tiene_precio': precio > 0,
        'sku_equivalente': sku_equivalente,
        'similitud_equivalente': similitud_equivalente,
        'alternativas': []
    }

def buscar_ugreen_producto(busqueda: str, ugreen_catalogo: Dict) -> Optional[List[Dict]]:
    """Busca productos en catálogo UGREEN"""
    if not ugreen_catalogo:
        return None
    
    df = ugreen_catalogo['df']
    col_sku = ugreen_catalogo['col_sku']
    col_desc = ugreen_catalogo['col_desc']
    col_stock = ugreen_catalogo.get('col_stock')
    
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
        
        precio_mayor = corregir_numero(row.get('Mayor', 0))
        precio_caja = corregir_numero(row.get('Caja', 0))
        precio_vip = corregir_numero(row.get('Vip', 0))
        
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
            },
            'stock': stock,
            'tiene_stock': stock > 0,
            'tiene_precio': precio_vip > 0 or precio_caja > 0 or precio_mayor > 0,
            'tipo': 'UGREEN'
        })
    
    return resultados
