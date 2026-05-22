# utils/constants.py - VERSIÓN COMPLETA

ALMACENES = {
    "YESSICA": {"orden": 1, "color": "verde", "tipo": "inmediato"},
    "APRI.004": {"orden": 2, "color": "naranja", "tipo": "inmediato"},
    "APRI.001": {"orden": 3, "color": "rojo", "tipo": "remoto"}
}

COLORES_BADGES = {
    "YESSICA": "#4CAF50",
    "APRI.004": "#FF9800", 
    "APRI.001": "#f44336",
    "UGREEN": "#00BCD4"
}

ROLES = {
    "admin": {"password": "qtc2026", "rol": "ADMIN", "nombre": "Administrador"},
    "kimberly": {"password": "kam2026", "rol": "KAM", "nombre": "Kimberly"},
    "vendedor": {"password": "ventas2026", "rol": "VENDEDOR", "nombre": "Vendedor"}
}

PRECIO_KEYS = ["P. VIP", "P. BOX", "P. IR"]

# ========== CONSTANTES PARA data_loader.py ==========
CATALOGO_COLUMNAS = ["SKU", "COD", "SAP", "NUMERO", "ARTICULO", "CODIGO"]
STOCK_COLUMNA_CLAVE = "Disponible"
COLUMNAS_A_IGNORAR = ["En stock", "Comprometido", "Solicitado", "Reservado"]

# ========== CONSTANTES PARA search_engine.py ==========
CATALOGO_COLUMNAS_BUSCAR = ["SKU", "COD", "SAP", "NUMERO", "ARTICULO", "CODIGO"]
DESCRIPCION_COLUMNAS = ["DESC", "DESCRIPCION", "NOMBRE", "PRODUCTO", "GOODS"]
