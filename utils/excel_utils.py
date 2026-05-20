# utils/excel_utils.py
"""Utilidades para procesamiento de archivos Excel"""

import re
import pandas as pd
import streamlit as st
from typing import Optional, Dict, List
from config.rules import SKU_COLUMNS, DESC_COLUMNS, PRICE_MAPPING


def corregir_numero(valor) -> float:
    """Convierte un valor a número, manejando formatos peruanos (S/, $, etc.)"""
    if pd.isna(valor) or str(valor).strip() in ["", "0", "0.0", "-"]:
        return 0.0
    
    s = str(valor).upper().replace('S/', '').replace('$', '').replace(' ', '').strip()
    
    # Manejar formato peruano (ej: 1,234.56 o 1.234,56)
    if ',' in s and '.' in s:
        s = s.replace(',', '')
    elif ',' in s:
        partes = s.split(',')
        if len(partes[-1]) <= 2:
            s = s.replace(',', '.')
        else:
            s = s.replace(',', '')
    
    s = re.sub(r'[^\d.]', '', s)
    
    try:
        return float(s)
    except:
        return 0.0


def limpiar_cabeceras(df: pd.DataFrame) -> pd.DataFrame:
    """Detecta y limpia cabeceras en archivos Excel"""
    for i in range(min(20, len(df))):
        fila = [str(x).upper() for x in df.iloc[i].values]
        if any(h in item for h in SKU_COLUMNS for item in fila):
            df.columns = [str(c).strip() for c in df.iloc[i]]
            return df.iloc[i+1:].reset_index(drop=True)
    return df


def cargar_archivo(uploaded_file) -> Optional[pd.DataFrame]:
    """Carga archivo Excel o CSV y limpia cabeceras"""
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
        st.error(f"Error al cargar archivo: {str(e)[:80]}")
        return None


def detectar_columna_sku(df: pd.DataFrame) -> str:
    """Detecta automáticamente la columna SKU en un DataFrame"""
    for col in df.columns:
        col_upper = str(col).upper()
        for posible in SKU_COLUMNS:
            if posible.upper() in col_upper:
                return col
    return df.columns[0]


def detectar_columna_descripcion(df: pd.DataFrame) -> str:
    """Detecta automáticamente la columna de descripción"""
    for col in df.columns:
        col_upper = str(col).upper()
        for posible in DESC_COLUMNS:
            if posible.upper() in col_upper:
                return col
    return None


def detectar_columnas_precio(df: pd.DataFrame) -> Dict:
    """Detecta columnas de precios (P. IR, P. BOX, P. VIP)"""
    precios = {}
    
    for key, patrones in PRICE_MAPPING.items():
        for col in df.columns:
            col_upper = str(col).upper()
            for patron in patrones:
                if patron in col_upper:
                    precios[key] = col
                    break
            if key in precios:
                break
    
    # Fallback: si no encuentra y hay columna 'PRECIO'
    if not precios and 'PRECIO' in [str(c).upper() for c in df.columns]:
        precios['P. VIP'] = 'PRECIO'
    
    return precios


def cargar_catalogo(archivo) -> Optional[Dict]:
    """Carga un catálogo completo (archivo + columnas detectadas)"""
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
    """Carga archivos de stock filtrando por modo (XIAOMI o UGREEN)"""
    stocks = []
    
    for archivo in archivos:
        try:
            xls = pd.ExcelFile(archivo)
            for hoja in xls.sheet_names:
                hoja_upper = hoja.upper()
                
                # Filtrar según modo
                if modo == "XIAOMI":
                    if not any(h in hoja_upper for h in ['APRI', 'YESSICA']):
                        continue
                else:  # UGREEN u otros
                    if 'APRI.001' not in hoja_upper:
                        continue
                
                df = pd.read_excel(archivo, sheet_name=hoja)
                df = limpiar_cabeceras(df)
                
                stocks.append({
                    'nombre': f"{archivo.name} [{hoja}]",
                    'df': df,
                    'col_sku': detectar_columna_sku(df),
                    'hoja': hoja
                })
                st.success(f"✅ {archivo.name} → {hoja}")
        except Exception as e:
            st.error(f"Error cargando {archivo.name}: {str(e)[:80]}")
    
    return stocks
