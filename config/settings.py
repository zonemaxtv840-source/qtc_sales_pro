# config/settings.py
"""Configuraciones globales de la aplicación"""

# Configuración de página
PAGE_CONFIG = {
    "page_title": "QTC Smart Sales Pro",
    "page_icon": "💼",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Credenciales de usuarios
USERS = {
    "admin": {"password": "qtc2026", "role": "ADMIN", "name": "Administrador"},
    "kimberly": {"password": "kam2026", "role": "KAM", "name": "Kimberly - Key Account Manager"},
    "vendedor": {"password": "ventas2026", "role": "VENDEDOR", "name": "Vendedor"}
}

# Role badges
ROLE_BADGES = {
    "ADMIN": "🔧",
    "KAM": "⭐",
    "VENDEDOR": "🛒",
    "INVITADO": "👤"
}

# Niveles de precio disponibles
PRICE_LEVELS = ["P. VIP", "P. BOX", "P. IR"]
