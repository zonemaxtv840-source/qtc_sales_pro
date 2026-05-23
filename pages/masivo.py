# pages/masivo.py - AÑADIR ESTA FUNCIÓN (si no existe)

def procesar_ugreen(texto_bulk):
    """Procesa lista masiva para UGREEN"""
    pedidos = extraer_pedidos_bulk(texto_bulk)
    
    if not pedidos:
        st.warning("No se encontraron productos válidos")
        return
    
    with st.spinner("Procesando UGREEN..."):
        resultados = []
        for pedido in pedidos:
            resultados_ugreen = buscar_ugreen_producto(pedido['sku'], st.session_state.ugreen_catalogo)
            if resultados_ugreen and len(resultados_ugreen) > 0:
                prod = resultados_ugreen[0]
                precio = prod['precios'].get(st.session_state.precio_key, 0)
                
                if precio > 0 and prod['tiene_stock']:
                    cantidad_cotizar = min(pedido['cantidad'], prod['stock'])
                    estado = "✅ OK"
                elif precio > 0 and not prod['tiene_stock']:
                    cantidad_cotizar = 0
                    estado = "❌ Sin stock"
                else:
                    cantidad_cotizar = 0
                    estado = "❌ Sin precio"
                
                resultados.append({
                    'sku': prod['sku'],
                    'descripcion': prod['descripcion'],
                    'precio': precio,
                    'stock_total': prod['stock'],
                    'tiene_stock': prod['tiene_stock'],
                    'tiene_precio': precio > 0,
                    'cantidad_solicitada': pedido['cantidad'],
                    'cantidad_cotizar': cantidad_cotizar,
                    'estado': estado,
                    'tipo': 'UGREEN'
                })
            else:
                resultados.append({
                    'sku': pedido['sku'],
                    'descripcion': f"SKU: {pedido['sku']}",
                    'precio': 0,
                    'stock_total': 0,
                    'tiene_stock': False,
                    'tiene_precio': False,
                    'cantidad_solicitada': pedido['cantidad'],
                    'cantidad_cotizar': 0,
                    'estado': "❌ No encontrado",
                    'tipo': 'UGREEN'
                })
        
        st.session_state.resultados_bulk = resultados
        st.success(f"✅ Procesados {len(pedidos)} productos UGREEN")
