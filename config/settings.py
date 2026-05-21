# config/settings.py
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

PRICE_LEVELS = ["P. VIP", "P. BOX", "P. IR"]
