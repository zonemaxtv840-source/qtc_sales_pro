import pandas as pd
import re

def corregir_numero(valor) -> float:
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

def limpiar_cabeceras(df: pd.DataFrame) -> pd.DataFrame:
    for i in range(min(20, len(df))):
        fila = [str(x).upper() for x in df.iloc[i].values]
        if any(h in item for h in ['SKU', 'COD', 'SAP', 'NUMERO', 'ARTICULO'] for item in fila):
            df.columns = [str(c).strip() for c in df.iloc[i]]
            return df.iloc[i+1:].reset_index(drop=True)
    return df

def normalizar_texto(texto: str) -> str:
    if not texto or pd.isna(texto):
        return ""
    texto = texto.lower().strip()
    
    correcciones = {
        "xioami": "xiaomi", "xiomi": "xiaomi", "xiamoi": "xiaomi",
        "earphone": "earphone", "earphones": "earphone",
    }
    for mal, bien in correcciones.items():
        texto = texto.replace(mal, bien)
    
    sufijos = [' - rn', ' - es', ' - us', ' - eu', ' - gl', ' - demo', ' - rr']
    for sufijo in sufijos:
        texto = texto.replace(sufijo, '')
    
    return texto.strip()

def formatear_moneda(valor: float) -> str:
    return f"S/ {valor:,.2f}"
