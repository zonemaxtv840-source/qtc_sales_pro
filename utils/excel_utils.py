# utils/excel_utils.py
import streamlit as st
import pandas as pd
import re
from difflib import SequenceMatcher


# ============================================
# FUNCIONES DE CARGA DE ARCHIVOS
# ============================================
def cargar_excel(archivo):
    """Carga cualquier Excel y limpia cabeceras"""
    try:
        if archivo.name.endswith('.csv'):
            df = pd.read_csv(archivo)
        else:
            df = pd.read_excel(archivo)
        
        # Limpiar cabeceras (buscar fila con SKU)
        for i in range(min(10, len(df))):
            fila = [str(x).upper() for x in df.iloc[i].values]
            if any('SKU' in x or 'COD' in x or 'SAP' in x or 'NUMERO' in x for x in fila):
                df.columns = df.iloc[i].astype(str).str.strip()
                df = df.iloc[i+1:].reset_index(drop=True)
                break
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return None


def cargar_catalogo(archivo):
    """Carga catálogo y detecta columnas"""
    df = cargar_excel(archivo)
    if df is None:
        return None
    
    # Detectar columnas
    col_sku = None
    col_desc = None
    col_precio_vip = None
    col_precio_box = None
    col_precio_ir = None
    
    for col in df.columns:
        col_upper = str(col).upper()
        if 'SKU' in col_upper or 'COD' in col_upper:
            col_sku = col
        elif 'DESC' in col_upper or 'PRODUCTO' in col_upper or 'NOMBRE' in col_upper:
            col_desc = col
        elif 'VIP' in col_upper:
            col_precio_vip = col
        elif 'BOX' in col_upper or 'CAJA' in col_upper:
            col_precio_box = col
        elif 'IR' in col_upper or 'MAYOR' in col_upper or 'MAYORISTA' in col_upper:
            col_precio_ir = col
    
    # Fallbacks
    if not col_sku:
        col_sku = df.columns[0]
    
    return {
        'nombre': archivo.name,
        'df': df,
        'col_sku': col_sku,
        'col_desc': col_desc,
        'col_vip': col_precio_vip,
        'col_box': col_precio_box,
        'col_ir': col_precio_ir
    }


def cargar_stock(archivo, modo="XIAOMI"):
    """Carga stock desde Excel - SOLO columna DISPONIBLE para APRI.001"""
    stocks = []
    try:
        xls = pd.ExcelFile(archivo)
        for hoja in xls.sheet_names:
            hoja_upper = hoja.upper()
            if modo == "XIAOMI":
                if not any(h in hoja_upper for h in ['YESSICA', 'APRI']):
                    continue
            
            df = pd.read_excel(archivo, sheet_name=hoja)
            
            # Detectar columnas
            col_sku = None
            col_cant = None
            col_desc = None
            
            for col in df.columns:
                col_upper = str(col).upper()
                if 'SKU' in col_upper or 'COD' in col_upper or 'NUMERO' in col_upper or 'ARTICULO' in col_upper:
                    col_sku = col
                elif 'CANT' in col_upper or 'STOCK' in col_upper:
                    col_cant = col
                elif 'DISPONIBLE' in col_upper:
                    col_cant = col  # PRIORIDAD: Disponible es la columna correcta
                elif 'DESC' in col_upper or 'DESCRIPCION' in col_upper:
                    col_desc = col
            
            # IMPORTANTE: Para APRI.001, SOLO usar columna DISPONIBLE
            if 'APRI.001' in hoja_upper:
                col_cant = None
                for col in df.columns:
                    if 'DISPONIBLE' in str(col).upper():
                        col_cant = col
                        break
            
            if col_sku and col_cant:
                stocks.append({
                    'hoja': hoja,
                    'df': df,
                    'col_sku': col_sku,
                    'col_cant': col_cant,
                    'col_desc': col_desc
                })
                st.success(f"✅ {hoja}: {len(df)} productos (usando columna: {col_cant})")
    except Exception as e:
        st.error(f"Error: {e}")
    
    return stocks


# ============================================
# FUNCIONES DE NORMALIZACIÓN Y SIMILITUD
# ============================================
def normalizar_texto(texto: str) -> str:
    """Normaliza texto para mejor comparación"""
    if not texto:
        return ""
    texto = texto.lower().strip()
    
    # Correcciones comunes
    correcciones = {
        "xioami": "xiaomi", "xiomi": "xiaomi", "xiamoi": "xiaomi",
        "earphone": "earphone", "earphones": "earphone",
        "type-c": "type c", "typec": "type c",
    }
    for mal, bien in correcciones.items():
        texto = texto.replace(mal, bien)
    
    # Eliminar sufijos
    sufijos = [' - rn', ' - es', ' - us', ' - eu', ' - gl', ' - demo', ' - rr']
    for sufijo in sufijos:
        texto = texto.replace(sufijo, '')
    
    return texto.strip()


def calcular_similitud(texto1: str, texto2: str) -> float:
    """Calcula similitud entre textos"""
    if not texto1 or not texto2:
        return 0.0
    texto1 = normalizar_texto(texto1)
    texto2 = normalizar_texto(texto2)
    if texto1 == texto2:
        return 100.0
    return SequenceMatcher(None, texto1, texto2).ratio() * 100


# ============================================
# FUNCIONES DE BÚSQUEDA
# ============================================
def corregir_numero(valor) -> float:
    """Convierte un valor a número"""
    if pd.isna(valor) or str(valor).strip() in ["", "0", "0.0", "-"]:
        return 0.0
    s = str(valor).upper().replace('S/', '').replace('$', '').replace(' ', '').strip()
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


def buscar_precio_por_sku(sku, catalogos, nivel_precio='P. VIP'):
    """Busca precio de un SKU en los catálogos"""
    for cat in catalogos:
        df = cat['df']
        col_sku = cat['col_sku']
        
        mask = df[col_sku].astype(str).str.strip().str.upper() == sku.upper()
        if mask.any():
            row = df[mask].iloc[0]
            
            if nivel_precio == 'P. VIP' and cat['col_vip']:
                precio = corregir_numero(row[cat['col_vip']])
                if precio > 0:
                    return precio
            elif nivel_precio == 'P. BOX' and cat['col_box']:
                precio = corregir_numero(row[cat['col_box']])
                if precio > 0:
                    return precio
            elif nivel_precio == 'P. IR' and cat['col_ir']:
                precio = corregir_numero(row[cat['col_ir']])
                if precio > 0:
                    return precio
            
            # Buscar cualquier columna numérica
            for col in df.columns:
                precio = corregir_numero(row[col])
                if 0 < precio < 10000:
                    return precio
            return 0.0
    return 0.0


def buscar_stock_por_sku(sku, stocks):
    """Busca stock de un SKU - APRI.001 SOLO usa columna DISPONIBLE"""
    stock = {'YESSICA': 0, 'APRI.004': 0, 'APRI.001': 0}
    
    for s in stocks:
        df = s['df']
        col_sku = s['col_sku']
        col_cant = s['col_cant']
        hoja = s['hoja'].upper()
        
        mask = df[col_sku].astype(str).str.strip().str.upper() == sku.upper()
        if mask.any():
            row = df[mask].iloc[0]
            try:
                cantidad = int(float(row[col_cant]))
            except:
                cantidad = 0
            
            if 'YESSICA' in hoja:
                stock['YESSICA'] += cantidad
            elif 'APRI.004' in hoja:
                stock['APRI.004'] += cantidad
            elif 'APRI.001' in hoja:
                stock['APRI.001'] += cantidad
    
    stock['TOTAL'] = stock['YESSICA'] + stock['APRI.004'] + stock['APRI.001']
    return stock


def buscar_producto(sku, catalogos, stocks, nivel_precio='P. VIP'):
    """Busca producto completo (precio + stock)"""
    precio = buscar_precio_por_sku(sku, catalogos, nivel_precio)
    stock = buscar_stock_por_sku(sku, stocks)
    
    # Buscar descripción
    descripcion = f"SKU: {sku}"
    for cat in catalogos:
        df = cat['df']
        col_sku = cat['col_sku']
        col_desc = cat.get('col_desc')
        if col_desc:
            mask = df[col_sku].astype(str).str.strip().str.upper() == sku.upper()
            if mask.any():
                descripcion = str(df[mask].iloc[0][col_desc])[:200]
                break
    
    return {
        'sku': sku,
        'descripcion': descripcion,
        'precio': precio,
        'stock': stock,
        'tiene_precio': precio > 0,
        'tiene_stock': stock['TOTAL'] > 0,
        'stock_inmediato': stock['YESSICA'] + stock['APRI.004'],
        'solo_apri001': stock['APRI.001'] > 0 and stock['YESSICA'] == 0 and stock['APRI.004'] == 0
    }


def buscar_por_descripcion(descripcion, catalogos, stocks, nivel_precio='P. VIP', umbral=70):
    """Busca productos por descripción (texto libre)"""
    desc_norm = normalizar_texto(descripcion)
    resultados = []
    
    for cat in catalogos:
        df = cat['df']
        col_sku = cat['col_sku']
        col_desc = cat.get('col_desc')
        
        if not col_desc:
            continue
        
        for _, row in df.iterrows():
            desc_cat = normalizar_texto(str(row[col_desc]))
            similitud = calcular_similitud(desc_norm, desc_cat)
            
            if similitud >= umbral:
                sku = str(row[col_sku]).strip()
                precio = buscar_precio_por_sku(sku, [cat], nivel_precio)
                stock = buscar_stock_por_sku(sku, stocks)
                
                resultados.append({
                    'sku': sku,
                    'descripcion': str(row[col_desc])[:150],
                    'similitud': similitud,
                    'precio': precio,
                    'stock': stock,
                    'tiene_precio': precio > 0,
                    'tiene_stock': stock['TOTAL'] > 0,
                    'fuente': cat['nombre'][:25]
                })
    
    resultados.sort(key=lambda x: x['similitud'], reverse=True)
    return resultados[:20]


def procesar_lista(texto, catalogos, stocks, nivel_precio='P. VIP'):
    """Procesa lista en formato SKU:CANTIDAD (si no hay cantidad, asume 1)"""
    resultados = []
    
    for linea in texto.strip().split('\n'):
        linea = linea.strip()
        if not linea:
            continue
        
        if ':' not in linea:
            sku = linea.upper()
            cantidad = 1
        else:
            parts = linea.split(':')
            if len(parts) != 2:
                continue
            sku = parts[0].strip().upper()
            try:
                cantidad = int(parts[1].strip())
                if cantidad <= 0:
                    cantidad = 1
            except:
                cantidad = 1
        
        prod = buscar_producto(sku, catalogos, stocks, nivel_precio)
        
        if prod['tiene_precio'] and prod['tiene_stock']:
            max_cotizable = prod['stock_inmediato'] if prod['stock_inmediato'] > 0 else prod['stock']['APRI.001']
            cantidad_cotizar = min(cantidad, max_cotizable)
            if cantidad_cotizar > 0:
                estado = "✅ OK"
            else:
                estado = "❌ Sin stock suficiente"
        elif prod['tiene_precio'] and not prod['tiene_stock']:
            cantidad_cotizar = 0
            estado = "❌ Sin stock"
        elif not prod['tiene_precio'] and prod['tiene_stock']:
            cantidad_cotizar = 0
            estado = "⚠️ Stock disponible pero sin precio"
        else:
            cantidad_cotizar = 0
            estado = "❌ Producto no encontrado"
        
        resultados.append({
            'sku': sku,
            'descripcion': prod['descripcion'],
            'cantidad_solicitada': cantidad,
            'cantidad_cotizar': cantidad_cotizar,
            'precio': prod['precio'],
            'estado': estado,
            'stock_yessica': prod['stock']['YESSICA'],
            'stock_apri004': prod['stock']['APRI.004'],
            'stock_apri001': prod['stock']['APRI.001'],
            'tiene_precio': prod['tiene_precio'],
            'tiene_stock': prod['tiene_stock']
        })
    
    return resultados
