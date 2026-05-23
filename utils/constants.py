# utils/constants.py
# Constantes globales del sistema

# Almacenes y colores
ALMACENES = {
    "YESSICA": {"orden": 1, "color": "#4CAF50", "tipo": "inmediato"},
    "APRI.004": {"orden": 2, "color": "#FF9800", "tipo": "inmediato"},
    "APRI.001": {"orden": 3, "color": "#f44336", "tipo": "remoto"}
}

COLORES_BADGES = {
    "YESSICA": "#4CAF50",
    "APRI.004": "#FF9800", 
    "APRI.001": "#f44336",
    "UGREEN": "#00BCD4"
}

# Credenciales
ROLES = {
    "admin": {"password": "qtc2026", "rol": "ADMIN", "nombre": "Administrador"},
    "kimberly": {"password": "kam2026", "rol": "KAM", "nombre": "Kimberly"},
    "vendedor": {"password": "ventas2026", "rol": "VENDEDOR", "nombre": "Vendedor"}
}

# Niveles de precio
PRECIO_KEYS = ["P. VIP", "P. BOX", "P. IR"]

# Columnas para detección
COLUMNAS_SKU = ['SKU', 'COD', 'SAP', 'NUMERO', 'ARTICULO', 'CODIGO']
COLUMNAS_DESCRIPCION = ['DESC', 'DESCRIPCION', 'NOMBRE', 'PRODUCTO', 'GOODS']
COLUMNAS_PRECIO = {
    'P. IR': ['IR', 'MAYORISTA', 'MAYOR'],
    'P. BOX': ['BOX', 'CAJA'],
    'P. VIP': ['VIP']
}

# Stock
COLUMNA_STOCK_DISPONIBLE = "Disponible"
COLUMNAS_STOCK_IGNORAR = ["En stock", "Comprometido", "Solicitado", "Reservado"]
