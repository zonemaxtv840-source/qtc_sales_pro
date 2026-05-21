# utils/file_handlers.py
import streamlit as st
import pandas as pd
from utils.excel_utils import cargar_archivo, detectar_columna_sku, detectar_columna_descripcion, detectar_columnas_precio


def cargar_ugreen_catalogo(archivo):
    """Carga específica para archivo UGREEN"""
    df = cargar_archivo(archivo)
    if df is None:
        return None
    
    col_sku = None
    col_desc = None
    col_mayor = None
    col_caja = None
    col_vip = None
    col_stock = None
    
    for col in df.columns:
        col_upper = str(col).upper()
        if 'SKU' in col_upper:
            col_sku = col
        elif 'DESCRITPION' in col_upper or 'DESCRIPCION' in col_upper or 'GOODS' in col_upper:
            col_desc = col
        elif col_upper == 'MAYOR':
            col_mayor = col
        elif col_upper == 'CAJA':
            col_caja = col
        elif col_upper == 'VIP':
            col_vip = col
        elif 'STOCK' in col_upper:
            col_stock = col
    
    if not col_sku:
        col_sku = df.columns[0]
    
    precios = {}
    if col_mayor:
        precios['P. IR'] = col_mayor
    if col_caja:
        precios['P. BOX'] = col_caja
    if col_vip:
        precios['P. VIP'] = col_vip
    
    return {
        'nombre': archivo.name,
        'df': df,
        'col_sku': col_sku,
        'col_desc': col_desc,
        'col_stock': col_stock,
        'precios': precios,
        'tipo': 'UGREEN'
    }
