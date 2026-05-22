import pandas as pd
import streamlit as st
from utils.constants import CATALOGO_COLUMNAS, STOCK_COLUMNA_CLAVE, COLUMNAS_A_IGNORAR

@st.cache_data
def cargar_catalogo(archivo):
    """Carga catálogo de precios desde Excel/CSV"""
    try:
        if archivo.name.endswith('.csv'):
            df = pd.read_csv(archivo)
        else:
            df = pd.read_excel(archivo, engine='openpyxl')
        
        # Normalizar columnas
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error cargando catálogo: {e}")
        return None

@st.cache_data
def cargar_stock_completo(archivo):
    """Carga stock desde Excel con múltiples hojas"""
    stock_dict = {}
    
    try:
        excel = pd.ExcelFile(archivo)
        for hoja in excel.sheet_names:
            # Solo procesar hojas que nos interesan
            if any(almacen in hoja for almacen in ["YESSICA", "APRI.004", "APRI.001"]):
                df = pd.read_excel(archivo, sheet_name=hoja)
                
                # Identificar columna de disponibilidad
                columna_stock = None
                for col in df.columns:
                    col_str = str(col).strip()
                    if STOCK_COLUMNA_CLAVE in col_str:
                        columna_stock = col
                        break
                
                if columna_stock:
                    # Mantener solo columnas necesarias
                    columnas_keep = []
                    for col in df.columns:
                        col_str = str(col).strip()
                        if any(ignorar in col_str for ignorar in COLUMNAS_A_IGNORAR):
                            continue
                        if "SKU" in col_str.upper() or col_str == columna_stock or "DESCRIP" in col_str.upper():
                            columnas_keep.append(col)
                    
                    if columnas_keep:
                        df_filtrado = df[columnas_keep].copy()
                        df_filtrado["ALMACEN"] = hoja.split()[0] if " " in hoja else hoja
                        stock_dict[hoja] = df_filtrado
                        st.info(f"📦 {hoja}: {len(df_filtrado)} productos con stock")
        
        return stock_dict
    except Exception as e:
        st.error(f"Error cargando stock: {e}")
        return None
