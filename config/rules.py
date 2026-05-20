# config/rules.py
"""Reglas de negocio para stock y cotizaciones"""

# Reglas APRI.001
APRI001_RULES = {
    "stock_minimo": 20,      # Stock mínimo para considerar transferencia
    "pedido_minimo": 5,      # Pedido mínimo para justificar transferencia
    "porcentaje_maximo": 0.15,  # 15% del stock total
    "tope_maximo": 100       # Máximo 100 unidades por pedido
}

# Margen de seguridad para stock inmediato
STOCK_SEGURITY_MARGIN = 2   # stock - 2 para YESSICA/APRI.004

# Umbral de similitud para búsqueda de SKUs equivalentes
SIMILARITY_THRESHOLD = 70.0  # 70%

# Columnas posibles para detectar en Excel
SKU_COLUMNS = ['SKU', 'COD', 'SAP', 'NUMERO', 'ARTICULO', 'CODIGO']
DESC_COLUMNS = ['DESC', 'DESCRIPCION', 'NOMBRE', 'PRODUCTO', 'GOODS', 'ARTICULO']
STOCK_COLUMNS = ['CANT', 'STOCK', 'DISPONIBLE', 'UNIDADES']

# Mapeo de precios por columna
PRICE_MAPPING = {
    'P. IR': ['IR', 'MAYORISTA', 'MAYOR'],
    'P. BOX': ['BOX', 'CAJA'],
    'P. VIP': ['VIP']
}
