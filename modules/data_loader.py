# modules/data_loader.py
# Carga de catálogos, stock y archivos UGREEN

import streamlit as st
import pandas as pd
from typing import List, Dict, Optional
from utils.helpers import limpiar_cabeceras, corregir_numero
from utils.constants import COLUMNAS_SKU, COLUMNAS_DESCRIPCION, COLUMNAS_PRECIO, COLUMNA_STOCK_DISPONIBLE

def detectar_columna_sku(df: pd.DataFrame) -> str:
    """Detecta la columna que contiene SKUs"""
    for col in df.columns:
        col_upper = str(col).upper()
        for patron in COLUMNAS_SKU:
            if patron.upper() in col_upper:
                return col
    return df.columns[0]

def detectar_columna_descripcion(df: pd.DataFrame) -> Optional[str]:
    """Detecta la columna de descripción"""
    for col in df.columns:
        col_upper = str(col).upper()
        for patron in COLUMNAS_DESCRIPCION:
            if patron.upper() in col_upper:
                return col
    return None

def detectar_columnas_precio(df: pd.DataFrame) -> Dict:
    """Detecta columnas de precios"""
    precios = {}
    
    for key, patrones in COLUMNAS_PRECIO.items():
        for col in df.columns:
            col_upper = str(col).upper()
            for patron in patrones:
                if patron in col_upper:
                    precios[key] = col
                    break
            if key in precios:
                break
    
    if not precios and 'PRECIO' in [str(c).upper() for c in df.columns]:
        precios['P. VIP'] = 'PRECIO'
    
    return precios

def cargar_archivo(uploaded_file) -> Optional[pd.DataFrame]:
    """Carga archivo Excel o CSV"""
    if uploaded_file is None:
        return None
    nombre = uploaded_file.name.lower()
    try:
        if nombre.endswith('.csv'):
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            except:
                df = pd.read_csv(uploaded_file, encoding='latin-1')
        else:
            df = pd.read_excel(uploaded_file)
        return limpiar_cabeceras(df)
    except Exception as e:
        st.error(f"Error cargando {nombre}: {str(e)[:80]}")
        return None

def cargar_catalogo(archivo) -> Optional[Dict]:
    """Carga catálogo de precios"""
    df = cargar_archivo(archivo)
    if df is None:
        return None
    
    return {
        'nombre': archivo.name,
        'df': df,
        'col_sku': detectar_columna_sku(df),
        'col_desc': detectar_columna_descripcion(df),
        'precios': detectar_columnas_precio(df)
    }

def cargar_stock(archivos, modo: str) -> List[Dict]:
    """
    Carga stock - SOLO usa la columna "Disponible" (o "Cantidad" como fallback)
    IGNORA: En stock, Comprometido, Solicitado
    """
    stocks = []
    
    for archivo in archivos:
        try:
            xls = pd.ExcelFile(archivo)
            for hoja in xls.sheet_names:
                hoja_upper = hoja.upper()
                if modo == "XIAOMI":
                    if not any(h in hoja_upper for h in ['APRI', 'YESSICA']):
                        continue
                else:
                    if 'APRI.001' not in hoja_upper:
                        continue
                
                df = pd.read_excel(archivo, sheet_name=hoja)
                df = limpiar_cabeceras(df)
                
                col_sku = detectar_columna_sku(df)
                col_cant = None
                
                # Buscar columna "Disponible" (PRIORIDAD MÁXIMA)
                for col in df.columns:
                    if 'DISPONIBLE' in str(col).upper():
                        col_cant = col
                        break
                
                # Si no hay "Disponible", buscar "Cantidad" (FALLBACK)
                if not col_cant:
                    for col in df.columns:
                        if 'CANTIDAD' in str(col).upper() or 'CANT' in str(col).upper():
                            col_cant = col
                            break
                
                if not col_cant:
                    st.error(f"❌ Hoja {hoja}: No se encontró columna 'Disponible' ni 'Cantidad'")
                    continue
                
                stocks.append({
                    'nombre': f"{archivo.name} [{hoja}]",
                    'df': df,
                    'col_sku': col_sku,
                    'col_cant': col_cant,
                    'hoja': hoja
                })
                st.success(f"✅ {archivo.name} → {hoja} (usando: {col_cant})")
                
        except Exception as e:
            st.error(f"Error en {archivo.name}: {str(e)[:80]}")
    
    return stocks

def cargar_ugreen_catalogo(archivo) -> Optional[Dict]:
    """Carga catálogo específico de UGREEN"""
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
        elif 'DESCRITPION' in col_upper or 'DESCRIPCION' in col_upper:
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
