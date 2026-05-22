import pandas as pd
from rapidfuzz import fuzz, process
from utils.helpers import limpiar_texto, normalizar_sku
from utils.constants import ALMACENES

class BusquedaProfesional:
    def __init__(self, catalogo_df, stock_dict):
        self.catalogo = catalogo_df
        self.stock = stock_dict
        self.ultima_busqueda = []
    
    def buscar(self, query, filtros=None):
        """Búsqueda profesional con fuzzy matching"""
        if not self.catalogo is not None or len(self.catalogo) == 0:
            return []
        
        query_limpia = limpiar_texto(query)
        if len(query_limpia) < 2:
            return []
        
        resultados = []
        
        # Buscar en SKU y descripción
        for idx, row in self.catalogo.iterrows():
            sku = normalizar_sku(str(row.get("SKU", "")))
            desc = limpiar_texto(str(row.get("Descripcion", "")))
            
            # Calcular similitud
            score_sku = fuzz.partial_ratio(query_limpia, sku.lower())
            score_desc = fuzz.partial_ratio(query_limpia, desc)
            score = max(score_sku, score_desc)
            
            if score > 60:
                # Obtener stock
                from modules.stock_engine import obtener_inventario_completo
                inventario = obtener_inventario_completo(sku, self.stock, self.catalogo)
                
                resultados.append({
                    "row": row,
                    "inventario": inventario,
                    "score": score
                })
        
        # Aplicar filtros
        if filtros:
            if filtros.get("solo_stock"):
                resultados = [r for r in resultados if r["inventario"]["tiene_stock"]]
            
            if filtros.get("precio_min"):
                resultados = [r for r in resultados if r["inventario"]["precio"] and r["inventario"]["precio"] >= filtros["precio_min"]]
            
            if filtros.get("precio_max"):
                resultados = [r for r in resultados if r["inventario"]["precio"] and r["inventario"]["precio"] <= filtros["precio_max"]]
        
        # Ordenar por score
        resultados.sort(key=lambda x: x["score"], reverse=True)
        self.ultima_busqueda = resultados[:50]  # Máximo 50 resultados
        
        return self.ultima_busqueda
    
    def autocompletar(self, query, limite=5):
        """Sugerencias en tiempo real"""
        if not query or len(query) < 2:
            return []
        
        query_limpia = limpiar_texto(query)
        sugerencias = set()
        
        for idx, row in self.catalogo.iterrows():
            sku = normalizar_sku(str(row.get("SKU", "")))
            desc = str(row.get("Descripcion", ""))[:50]
            
            if query_limpia in sku.lower() or query_limpia in limpiar_texto(desc):
                sugerencias.add(f"{sku} - {desc[:40]}")
                if len(sugerencias) >= limite:
                    break
        
        return list(sugerencias)
