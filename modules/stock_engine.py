import pandas as pd
from utils.constants import ALMACENES
from utils.helpers import normalizar_sku, limpiar_texto

def buscar_stock_por_sku(sku, stock_dict):
    """Retorna stock SEPARADO por almacén (NO suma)"""
    sku_norm = normalizar_sku(sku)
    resultado = {almacen: 0 for almacen in ALMACENES.keys()}
    
    if not stock_dict:
        return resultado
    
    for hoja, df in stock_dict.items():
        almacen_nombre = hoja.split()[0] if " " in hoja else hoja
        if almacen_nombre not in resultado:
            continue
        
        col_sku = None
        for col in df.columns:
            if "SKU" in str(col).upper():
                col_sku = col
                break
        
        if col_sku:
            df['SKU_NORM'] = df[col_sku].apply(normalizar_sku)
            coincidencia = df[df['SKU_NORM'] == sku_norm]
            if not coincidencia.empty:
                col_stock = None
                for col in df.columns:
                    if "Disponible" in str(col):
                        col_stock = col
                        break
                if col_stock:
                    try:
                        resultado[almacen_nombre] = int(coincidencia.iloc[0][col_stock])
                    except:
                        resultado[almacen_nombre] = 0
    
    return resultado

def buscar_sku_por_descripcion(descripcion, catalogo_df):
    """Busca SKU alternativo por descripción similar"""
    if catalogo_df is None:
        return None
    
    desc_limpia = limpiar_texto(descripcion)
    mejor_match = None
    mejor_score = 0
    
    for idx, row in catalogo_df.iterrows():
        desc_catalogo = limpiar_texto(str(row.get("Descripcion", "")))
        # Búsqueda simple de palabras clave
        score = sum(1 for palabra in desc_limpia.split() if palabra in desc_catalogo)
        if score > mejor_score and score > 0:
            mejor_score = score
            mejor_match = row
    
    return mejor_match["SKU"] if mejor_match is not None else None

def obtener_inventario_completo(sku, stock_dict, catalogo_df):
    """Integra stock + precio + SKU equivalente"""
    stock = buscar_stock_por_sku(sku, stock_dict)
    tiene_stock = sum(stock.values()) > 0
    
    # Buscar precio
    precio = None
    if catalogo_df is not None:
        sku_norm = normalizar_sku(sku)
        producto = catalogo_df[catalogo_df["SKU"].astype(str).str.upper() == sku_norm]
        
        if producto.empty and not tiene_stock:
            # Buscar por descripción si no hay precio
            sku_alternativo = buscar_sku_por_descripcion(sku, catalogo_df)
            if sku_alternativo:
                producto = catalogo_df[catalogo_df["SKU"].astype(str).str.upper() == normalizar_sku(sku_alternativo)]
        
        if not producto.empty:
            precio = producto.iloc[0].get("Precio VIP", producto.iloc[0].get("Precio", 0))
    
    return {
        "sku": sku,
        "stock": stock,
        "precio": precio,
        "tiene_stock": tiene_stock,
        "stock_total": sum(stock.values())
    }
