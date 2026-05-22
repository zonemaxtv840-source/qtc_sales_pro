# Constantes globales del sistema
ALMACENES = {
    "YESSICA": {"orden": 1, "color": "verde", "tipo": "inmediato"},
    "APRI.004": {"orden": 2, "color": "naranja", "tipo": "inmediato"},
    "APRI.001": {"orden": 3, "color": "rojo", "tipo": "remoto"}
}

COLORES_BADGES = {
    "YESSICA": "#27ae60",
    "APRI.004": "#e67e22", 
    "APRI.001": "#e74c3c"
}

ROLES = {
    "admin": {"password": "qtc2026", "permisos": ["full"]},
    "kimberly": {"password": "kam2026", "permisos": ["cotizar", "exportar"]},
    "vendedor": {"password": "ventas2026", "permisos": ["cotizar"]}
}

CATALOGO_COLUMNAS = ["SKU", "Descripcion", "Precio VIP", "Precio Sugerido", "Familia", "Marca"]
STOCK_COLUMNA_CLAVE = "Disponible"
COLUMNAS_A_IGNORAR = ["En stock", "Comprometido", "Solicitado", "Reservado"]
