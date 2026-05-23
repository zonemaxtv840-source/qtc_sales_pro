# modules/search_engine.py
# Motor de búsqueda profesional con fuzzy matching

import streamlit as st
import pandas as pd
from typing import List, Dict, Optional
from difflib import SequenceMatcher
from utils.helpers import normalizar_texto, corregir_numero
from modules.stock_engine import buscar_stock_para_sku

# Intentar importar rapidfuzz para mejor búsqueda, fallback a difflib
try:
    from rapidfuzz import fuzz, process
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False

def calcular_similitud_profesional(texto1: str, texto2: str) -> float:
    """Calcula similitud entre textos usando rapidfuzz si está disponible"""
    if not texto1 or not texto2:
        return 0.0
    
    texto1 = normalizar_texto(texto1)
    texto2 = normalizar_texto(texto2)
    
    if RAPIDFUZZ_AVAILABLE:
        # Usar rapidfuzz (más rápido y preciso)
        return fuzz.ratio(texto1, texto2)
    else:
        # Fallback a difflib
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
        return round((jaccard * 0.6 + sequence_match * 0.4) * 100, 1)

def buscar_productos_profesional(
    query: str, 
    catalogos: List[Dict], 
    stocks: List[Dict], 
    precio_key: str,
    filtros: Optional[Dict] = None
) -> List[Dict]:
    """
    Búsqueda profesional con:
    - Fuzzy matching (tolerancia a errores)
    - Búsqueda en SKU y descripción
    - Filtros por stock y precio
    - Ordenamiento por relevancia
    """
    if not query or len(query) < 2:
        return []
    
    query_limpia = normalizar_texto(query)
    resultados = []
    
    for cat in catalogos:
        df = cat['df']
        col_sku = cat['col_sku']
        col_desc = cat.get('col_desc')
        
        for idx, row in df.iterrows():
            sku = str(row[col_sku]).strip().upper()
            desc = normalizar_texto(str(row[col_desc]) if col_desc else "")
            
            # Calcular scores de coincidencia
            score_sku = calcular_similitud_profesional(query_limpia, sku.lower())
            score_desc = calcular_similitud_profesional(query_limpia, desc) if desc else 0
            score_total = max(score_sku, score_desc)
            
            # Umbral de relevancia (70% para ser considerado)
            if score_total >= 70:
                # Obtener precio
                precio = 0
                if precio_key in cat.get('precios', {}):
                    col_precio = cat['precios'][precio_key]
                    precio = corregir_numero(row[col_precio])
                
                # Obtener stock
                stock_info = buscar_stock_para_sku(sku, stocks)
                
                resultados.append({
                    'sku': sku,
                    'descripcion': str(row[col_desc])[:200] if col_desc else f"SKU: {sku}",
                    'precio': precio,
                    'stock_yessica': stock_info['yessica'],
                    'stock_apri004': stock_info['apri004'],
                    'stock_apri001': stock_info['apri001'],
                    'stock_total': stock_info['total'],
                    'tiene_stock': stock_info['total'] > 0,
                    'tiene_precio': precio > 0,
                    'score': score_total,
                    'catalogo': cat['nombre'][:30]
                })
    
    # Eliminar duplicados por SKU (mantener el de mayor score)
    vistos = {}
    for r in resultados:
        if r['sku'] not in vistos or r['score'] > vistos[r['sku']]['score']:
            vistos[r['sku']] = r
    resultados = list(vistos.values())
    
    # Aplicar filtros
    if filtros:
        if filtros.get('solo_stock'):
            resultados = [r for r in resultados if r['tiene_stock']]
        if filtros.get('solo_precio'):
            resultados = [r for r in resultados if r['tiene_precio']]
        if filtros.get('precio_min'):
            resultados = [r for r in resultados if r['precio'] >= filtros['precio_min']]
        if filtros.get('precio_max'):
            resultados = [r for r in resultados if r['precio'] <= filtros['precio_max']]
    
    # Ordenar por relevancia (score más alto primero)
    resultados.sort(key=lambda x: (-x['score'], -x['tiene_stock'], -x['tiene_precio']))
    
    return resultados[:100]  # Máximo 100 resultados

def autocompletar_busqueda(query: str, catalogos: List[Dict], limite: int = 5) -> List[Dict]:
    """
    Sugerencias de autocompletado en tiempo real
    """
    if not query or len(query) < 2:
        return []
    
    query_limpia = normalizar_texto(query)
    sugerencias = []
    
    for cat in catalogos:
        df = cat['df']
        col_sku = cat['col_sku']
        col_desc = cat.get('col_desc')
        
        for _, row in df.iterrows():
            sku = str(row[col_sku]).strip().upper()
            desc = normalizar_texto(str(row[col_desc]) if col_desc else "")
            
            # Coincidencia exacta o parcial
            if query_limpia in sku.lower() or (desc and query_limpia in desc):
                sugerencias.append({
                    'sku': sku,
                    'descripcion': str(row[col_desc])[:60] if col_desc else sku,
                    'tipo': 'SKU' if query_limpia in sku.lower() else 'Descripción'
                })
                if len(sugerencias) >= limite:
                    break
        if len(sugerencias) >= limite:
            break
    
    return sugerencias

def obtener_productos_destacados(catalogos: List[Dict], stocks: List[Dict], limite: int = 10) -> List[Dict]:
    """
    Obtiene productos con stock disponible para mostrar como destacados
    """
    destacados = []
    
    for cat in catalogos:
        df = cat['df'].head(30)
        col_sku = cat['col_sku']
        col_desc = cat.get('col_desc')
        
        for _, row in df.iterrows():
            sku = str(row[col_sku]).strip().upper()
            stock_info = buscar_stock_para_sku(sku, stocks)
            
            if stock_info['total'] > 0:
                destacados.append({
                    'sku': sku,
                    'descripcion': str(row[col_desc])[:80] if col_desc else sku,
                    'stock_total': stock_info['total']
                })
                if len(destacados) >= limite:
                    break
        if len(destacados) >= limite:
            break
    
    return destacados
