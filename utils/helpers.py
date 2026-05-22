import pandas as pd
import re

def limpiar_texto(texto):
    """Limpia texto para comparaciones"""
    if pd.isna(texto):
        return ""
    texto = str(texto).lower().strip()
    texto = re.sub(r'[^\w\s]', '', texto)
    return texto

def normalizar_sku(sku):
    """Normaliza SKU (mayúsculas, sin espacios)"""
    if pd.isna(sku):
        return ""
    return str(sku).upper().strip()

def formatear_moneda(valor):
    """Formatea número como moneda S/"""
    try:
        return f"S/ {float(valor):,.2f}"
    except:
        return "S/ 0.00"

def extraer_cantidad(texto):
    """Extrae cantidad de formato SKU:CANTIDAD"""
    if ":" not in texto:
        return (texto.strip(), 1)
    partes = texto.split(":", 1)
    try:
        cantidad = int(partes[1])
    except:
        cantidad = 1
    return (partes[0].strip(), cantidad)
