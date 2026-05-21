# config/rules.py
APRI001_RULES = {
    "stock_minimo": 20,
    "pedido_minimo": 5,
    "porcentaje_maximo": 0.15,
    "tope_maximo": 100
}

STOCK_SEGURITY_MARGIN = 2
SIMILARITY_THRESHOLD = 70.0

SKU_COLUMNS = ['SKU', 'COD', 'SAP', 'NUMERO', 'ARTICULO', 'CODIGO']
DESC_COLUMNS = ['DESC', 'DESCRIPCION', 'NOMBRE', 'PRODUCTO', 'GOODS', 'ARTICULO']
STOCK_COLUMNS = ['CANT', 'STOCK', 'DISPONIBLE', 'UNIDADES']
