# app.py - QTC Smart Sales Pro v5.0 (BÚSQUEDA AVANZADA & ESTABILIZADO)
# Soporte Inteligente: XIAOMI, UGREEN, OTRAS MARCAS
# Fixes aplicados: Carrito seguro, Búsqueda multicriterio, Control de stock preciso

import streamlit as st
import pandas as pd
import re
import io
from datetime import datetime
import warnings
from typing import List, Dict, Optional
from difflib import SequenceMatcher

warnings.filterwarnings('ignore')

# ============================================
# CONFIGURACIÓN Y ESTILOS
# ============================================

st.set_page_config(page_title="QTC Smart Sales Pro", page_icon="💼", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0d47a1 0%, #1565c0 50%, #1e88e5 100%); }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #f8a35e 0%, #e87a2d 50%, #d45a1a 100%); border-right: 1px solid #ffcc80; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .stMarkdown, .stText, .stNumberInput label, .stSelectbox label { color: #ffffff !important; }
    h1, h2, h3 { color: #ffffff !important; }
    
    /* Cards con texto negro */
    div[style*="background:white"], div[style*="background:#ffffff"], div[style*="border-radius:16px"] { color: #1a1a2e !important; }
    div[style*="background:white"] *, div[style*="background:#ffffff"] *, div[style*="border-radius:16px"] * { color: #1a1a2e !important; }
    
    /* Excepciones */
    .badge-yessica, .badge-apri004, .badge-apri001, .badge-ugreen, .badge-otras,
    .badge-yessica *, .badge-apri004 *, .badge-apri001 *, .badge-ugreen *, .badge-otras * { color: white !important; }
    .precio-texto { color: #e67e22 !important; font-weight: bold; }
    
    /* Badges */
    .badge-yessica { background: #4CAF50; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; display: inline-block; margin: 2px; }
    .badge-apri004 { background: #FF9800; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; display: inline-block; margin: 2px; }
    .badge-apri001 { background: #f44336; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; display: inline-block; margin: 2px; }
    .badge-ugreen { background: #00BCD4; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; display: inline-block; margin: 2px; }
    .badge-otras { background: #9C27B0; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; display: inline-block; margin: 2px; }
    
    .counter-summary { background: rgba(0,0,0,0.3); border-radius: 12px; padding: 1rem; margin-bottom: 1rem; display: flex; justify-content: space-around; flex-wrap: wrap; }
    .counter-item { text-align: center; padding: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# ============================================
# FUNCIONES NÚCLEO Y LIMPIEZA
# ============================================

def corregir_numero(valor) -> float:
    if pd.isna(valor) or str(valor).strip() in ["", "0", "0.0", "-"]: return 0.0
    s = str(valor).upper().replace('S/', '').replace('$', '').replace(' ', '').strip()
    if ',' in s and '.' in s: s = s.replace(',', '')
    elif ',' in s:
        partes = s.split(',')
        if len(partes[-1]) <= 2: s = s.replace(',', '.')
        else: s = s.replace(',', '')
    s = re.sub(r'[^\d.]', '', s)
    try: return float(s)
    except: return 0.0

def limpiar_cabeceras(df: pd.DataFrame) -> pd.DataFrame:
    for i in range(min(20, len(df))):
        fila = [str(x).upper() for x in df.iloc[i].values]
        if any(h in item for h in ['SKU', 'COD', 'SAP', 'NUMERO', 'ARTICULO'] for item in fila):
            df.columns = [str(c).strip() for c in df.iloc[i]]
            return df.iloc[i+1:].reset_index(drop=True)
    return df

def cargar_archivo(uploaded_file) -> Optional[pd.DataFrame]:
    try:
        if uploaded_file.name.lower().endswith('.csv'):
            try: df = pd.read_csv(uploaded_file, encoding='utf-8')
            except: df = pd.read_csv(uploaded_file, encoding='latin-1')
        else: df = pd.read_excel(uploaded_file)
        return limpiar_cabeceras(df)
    except Exception as e:
        st.error(f"Error cargando {uploaded_file.name}: {str(e)[:80]}")
        return None

def detectar_columnas(df: pd.DataFrame, tipo: str) -> str:
    diccionario = {
        'sku': ['SKU', 'COD', 'SAP', 'NUMERO', 'ARTICULO', 'CODIGO'],
        'desc': ['DESC', 'DESCRIPCION', 'NOMBRE', 'PRODUCTO', 'GOODS'],
        'stock': ['DISPONIBLE', 'CANTIDAD', 'CANT', 'STOCK']
    }
    for col in df.columns:
        col_upper = str(col).upper()
        if any(posible in col_upper for posible in diccionario.get(tipo, [])):
            return col
    return df.columns[0] if tipo == 'sku' else None

def detectar_columnas_precio(df: pd.DataFrame) -> Dict:
    precios, mapeo = {}, {'P. IR': ['IR', 'MAYORISTA', 'MAYOR'], 'P. BOX': ['BOX', 'CAJA'], 'P. VIP': ['VIP']}
    for key, patrones in mapeo.items():
        for col in df.columns:
            if any(patron in str(col).upper() for patron in patrones):
                precios[key] = col
                break
    if not precios and 'PRECIO' in [str(c).upper() for c in df.columns]:
        precios['P. VIP'] = 'PRECIO'
    return precios

# ============================================
# LÓGICA DE CATÁLOGOS Y STOCK
# ============================================

def cargar_catalogo(archivo) -> Optional[Dict]:
    df = cargar_archivo(archivo)
    if df is None: return None
    return {
        'nombre': archivo.name, 'df': df,
        'col_sku': detectar_columnas(df, 'sku'),
        'col_desc': detectar_columnas(df, 'desc'),
        'precios': detectar_columnas_precio(df)
    }

def cargar_stock(archivos, modo: str) -> List[Dict]:
    stocks = []
    for archivo in archivos:
        try:
            xls = pd.ExcelFile(archivo)
            for hoja in xls.sheet_names:
                hoja_upper = hoja.upper()
                if modo == "XIAOMI" and not any(h in hoja_upper for h in ['APRI', 'YESSICA']): continue
                
                df = limpiar_cabeceras(pd.read_excel(archivo, sheet_name=hoja))
                col_cant = detectar_columnas(df, 'stock')
                
                if not col_cant:
                    st.warning(f"⚠️ Hoja {hoja}: Sin columna de stock válida")
                    continue
                
                stocks.append({
                    'nombre': f"{archivo.name} [{hoja}]", 'df': df,
                    'col_sku': detectar_columnas(df, 'sku'), 'col_cant': col_cant, 'hoja': hoja
                })
        except Exception as e: st.error(f"Error en {archivo.name}: {str(e)[:80]}")
    return stocks

def buscar_stock_para_sku(sku: str, stocks: List[Dict], modo: str) -> Dict:
    sku_limpio = str(sku).strip().upper()
    resultado = {'yessica': 0, 'apri004': 0, 'apri001': 0, 'otros': 0, 'total': 0}
    
    for stock in stocks:
        df, col_sku, col_cant = stock['df'], stock['col_sku'], stock['col_cant']
        mask = df[col_sku].astype(str).str.strip().str.upper() == sku_limpio
        
        if mask.any():
            cantidad = int(corregir_numero(df[mask].iloc[0][col_cant]))
            hoja = stock['hoja'].upper()
            
            if modo == "XIAOMI":
                if 'YESSICA' in hoja: resultado['yessica'] = cantidad
                elif 'APRI.004' in hoja: resultado['apri004'] = cantidad
                elif 'APRI.001' in hoja: resultado['apri001'] = cantidad
            else:
                resultado['otros'] += cantidad
                
    resultado['total'] = sum([resultado['yessica'], resultado['apri004'], resultado['apri001'], resultado['otros']])
    return resultado

# ============================================
# BÚSQUEDA INTELIGENTE (MEJORADA)
# ============================================

def crear_mascara_busqueda_inteligente(df: pd.DataFrame, col_sku: str, col_desc: str, busqueda: str) -> pd.Series:
    """Busca por múltiples tokens (palabras clave) en cualquier orden."""
    tokens = [t.strip() for t in str(busqueda).split() if len(t.strip()) > 1]
    if not tokens: return pd.Series([False] * len(df))
    
    mask = pd.Series([True] * len(df))
    for token in tokens:
        mask_token = df[col_sku].astype(str).str.contains(token, case=False, na=False)
        if col_desc:
            mask_token |= df[col_desc].astype(str).str.contains(token, case=False, na=False)
        mask &= mask_token
    return mask

def buscar_catalogo_general(busqueda: str, catalogos: List[Dict], stocks: List[Dict], precio_key: str, modo: str) -> List[Dict]:
    productos_encontrados = {}
    
    for cat in catalogos:
        df = cat['df']
        col_sku, col_desc = cat['col_sku'], cat.get('col_desc')
        mask = crear_mascara_busqueda_inteligente(df, col_sku, col_desc, busqueda)
        
        for _, row in df[mask].iterrows():
            sku = str(row[col_sku]).strip().upper()
            if sku not in productos_encontrados:
                descripcion = str(row[col_desc])[:200] if col_desc else f"SKU: {sku}"
                stock_info = buscar_stock_para_sku(sku, stocks, modo)
                
                productos_encontrados[sku] = {
                    'sku': sku, 'descripcion': descripcion, 'precio': 0.0,
                    'stock_yessica': stock_info['yessica'], 'stock_apri004': stock_info['apri004'],
                    'stock_apri001': stock_info['apri001'], 'stock_otros': stock_info['otros'],
                    'stock_total': stock_info['total'], 'tiene_stock': stock_info['total'] > 0,
                    'tipo': modo
                }
            
            # Actualizar precio si es mayor (prioriza listas de precios actualizadas)
            if precio_key in cat.get('precios', {}):
                col_precio = cat['precios'][precio_key]
                precio_actual = corregir_numero(row[col_precio])
                if precio_actual > productos_encontrados[sku]['precio']:
                    productos_encontrados[sku]['precio'] = precio_actual
                    productos_encontrados[sku]['tiene_precio'] = True

    resultados = list(productos_encontrados.values())
    resultados.sort(key=lambda x: (-x['tiene_stock'], -x.get('tiene_precio', False)))
    return resultados

def buscar_ugreen_producto(busqueda: str, ugreen_catalogo: Dict) -> List[Dict]:
    if not ugreen_catalogo: return []
    
    df, col_sku, col_desc = ugreen_catalogo['df'], ugreen_catalogo['col_sku'], ugreen_catalogo['col_desc']
    col_stock = ugreen_catalogo.get('col_stock')
    precios_map = ugreen_catalogo.get('precios', {})
    
    mask = crear_mascara_busqueda_inteligente(df, col_sku, col_desc, busqueda)
    resultados = []
    
    for _, row in df[mask].iterrows():
        sku = str(row[col_sku]).strip().upper()
        stock = int(corregir_numero(row[col_stock])) if col_stock and pd.notna(row[col_stock]) else 0
        
        precio_ir = corregir_numero(row.get(precios_map.get('P. IR', 'N/A'), 0))
        precio_box = corregir_numero(row.get(precios_map.get('P. BOX', 'N/A'), 0))
        precio_vip = corregir_numero(row.get(precios_map.get('P. VIP', 'N/A'), 0))
        
        resultados.append({
            'sku': sku,
            'descripcion': str(row[col_desc])[:200] if col_desc else f"SKU: {sku}",
            'precios': {'P. IR': precio_ir, 'P. BOX': precio_box, 'P. VIP': precio_vip},
            'stock_total': stock, 'tiene_stock': stock > 0,
            'tiene_precio': any(p > 0 for p in [precio_ir, precio_box, precio_vip]),
            'tipo': 'UGREEN'
        })
    return resultados

# ============================================
# EXPORTACIÓN
# ============================================

def generar_excel(items: List[Dict], cliente: str, ruc: str) -> bytes:
    output = io.BytesIO()
    df = pd.DataFrame(items)
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Cotizacion', index=False, startrow=6)
        ws = writer.sheets['Cotizacion']
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        
        border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
        ws['A1'] = 'QTC SMART SALES PRO'
        ws['A1'].font = Font(bold=True, size=14)
        ws['A3'], ws['B3'] = 'FECHA:', datetime.now().strftime("%d/%m/%Y %H:%M")
        ws['A4'], ws['B4'] = 'CLIENTE:', cliente.upper()
        ws['A5'], ws['B5'] = 'RUC:', ruc
        
        headers = ['SKU', 'DESCRIPCIÓN', 'CANTIDAD', 'PRECIO UNIT.', 'TOTAL']
        for i, header in enumerate(headers, start=1):
            cell = ws.cell(row=7, column=i, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="e67e22", end_color="e67e22", fill_type="solid")
            cell.alignment = Alignment(horizontal="center")
            cell.border = border
        
        for r_idx, item in enumerate(items, start=8):
            ws.cell(row=r_idx, column=1, value=item['sku']).border = border
            ws.cell(row=r_idx, column=2, value=item['descripcion']).border = border
            ws.cell(row=r_idx, column=3, value=item['cantidad']).border = border
            c_precio = ws.cell(row=r_idx, column=4, value=item['precio'])
            c_precio.number_format, c_precio.border = '"S/." #,##0.00', border
            c_total = ws.cell(row=r_idx, column=5, value=item['total'])
            c_total.number_format, c_total.border = '"S/." #,##0.00', border
        
        t_row = len(items) + 8
        t_lbl = ws.cell(row=t_row, column=4, value='TOTAL S/.')
        t_lbl.font, t_lbl.fill, t_lbl.border = Font(bold=True, color="FFFFFF"), PatternFill(start_color="e67e22", end_color="e67e22", fill_type="solid"), border
        t_val = ws.cell(row=t_row, column=5, value=sum(i['total'] for i in items))
        t_val.number_format, t_val.border = '"S/." #,##0.00', border
        
        ws.column_dimensions['A'].width, ws.column_dimensions['B'].width = 22, 110
        ws.column_dimensions['C'].width, ws.column_dimensions['D'].width, ws.column_dimensions['E'].width = 12, 18, 18
    return output.getvalue()

# ============================================
# INICIALIZACIÓN
# ============================================

for key in ['auth', 'catalogos', 'stocks', 'carrito', 'ugreen_catalogo']:
    if key not in st.session_state:
        st.session_state[key] = [] if key in ['catalogos', 'stocks', 'carrito'] else False if key == 'auth' else None
if 'modo' not in st.session_state: st.session_state.modo = "XIAOMI"
if 'precio_key' not in st.session_state: st.session_state.precio_key = "P. VIP"

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div style="background:rgba(255,255,255,0.95);border-radius:20px;padding:2rem;text-align:center;"><h2>QTC Smart Sales Pro</h2><p style="color:#666;">Ingreso al Sistema</p></div>', unsafe_allow_html=True)
        user = st.text_input("👤 Usuario", placeholder="admin / vendedor")
        pw = st.text_input("🔒 Contraseña", type="password")
        if st.button("🚀 Ingresar", use_container_width=True):
            if (user == "admin" and pw == "qtc2026") or (user == "vendedor" and pw == "ventas2026"):
                st.session_state.auth, st.session_state.user_role, st.session_state.user_name = True, "ADMIN" if user=="admin" else "VENDEDOR", user.capitalize()
                st.rerun()
            else: st.error("❌ Credenciales incorrectas")
    st.stop()

# ============================================
# UI PRINCIPAL
# ============================================

col1, col2, col3 = st.columns([1, 5, 2])
with col2: st.markdown("## QTC Smart Sales Pro")
with col3:
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.auth, st.session_state.carrito = False, []
        st.rerun()

with st.sidebar:
    st.markdown("### 🎯 Configuración")
    st.session_state.modo = st.radio("📌 Marca / Modo", ["XIAOMI", "UGREEN", "OTRAS MARCAS"], index=["XIAOMI", "UGREEN", "OTRAS MARCAS"].index(st.session_state.modo))
    st.session_state.precio_key = st.radio("💰 Nivel de precio", ["P. VIP", "P. BOX", "P. IR"])
    
    st.markdown("### 📂 Archivos")
    if st.session_state.modo in ["XIAOMI", "OTRAS MARCAS"]:
        archivos_cat = st.file_uploader("Catálogos (Excel/CSV)", type=['xlsx', 'xls', 'csv'], accept_multiple_files=True)
        if archivos_cat:
            st.session_state.catalogos = [c for c in (cargar_catalogo(a) for a in archivos_cat) if c]
            st.success(f"✅ {len(st.session_state.catalogos)} catálogos listos")
            
        archivos_stock = st.file_uploader("Stock (Excel)", type=['xlsx', 'xls'], accept_multiple_files=True)
        if archivos_stock:
            st.session_state.stocks = cargar_stock(archivos_stock, st.session_state.modo)
            st.success(f"✅ Stock listo")
            
    elif st.session_state.modo == "UGREEN":
        archivo_ugreen = st.file_uploader("Catálogo UGREEN", type=['xlsx', 'xls'])
        if archivo_ugreen:
            st.session_state.ugreen_catalogo = cargar_catalogo(archivo_ugreen)
            st.session_state.ugreen_catalogo['col_stock'] = detectar_columnas(st.session_state.ugreen_catalogo['df'], 'stock')
            st.success("✅ UGREEN listo")

# ============================================
# TABS
# ============================================

tab1, tab2, tab3 = st.tabs(["📦 MODO MASIVO", "🔍 BÚSQUEDA INTELIGENTE", f"🛒 CARRITO ({len(st.session_state.carrito)})"])

with tab2:
    st.markdown("### 🔍 Búsqueda Multicriterio")
    busqueda = st.text_input("", placeholder="Ej: 'audifonos bluetooth' (Busca en cualquier orden)")
    
    if busqueda and len(busqueda) >= 2:
        with st.spinner("🔍 Rastreando base de datos..."):
            resultados = []
            if st.session_state.modo in ["XIAOMI", "OTRAS MARCAS"] and st.session_state.catalogos:
                resultados = buscar_catalogo_general(busqueda, st.session_state.catalogos, st.session_state.stocks, st.session_state.precio_key, st.session_state.modo)
            elif st.session_state.modo == "UGREEN" and st.session_state.ugreen_catalogo:
                resultados = buscar_ugreen_producto(busqueda, st.session_state.ugreen_catalogo)
                for r in resultados: r['precio'] = r['precios'].get(st.session_state.precio_key, 0)
            
            if resultados:
                st.success(f"✅ {len(resultados)} coincidencias")
                for prod in resultados:
                    precio_str = f"S/ {prod['precio']:,.2f}" if prod.get('precio', 0) > 0 else "Consultar Precio"
                    color_borde = "#4CAF50" if prod['tiene_stock'] and prod.get('precio',0)>0 else "#f44336" if prod['tiene_stock'] else "#9e9e9e"
                    
                    if prod['tipo'] == 'XIAOMI':
                        badge_stock = f'<span class="badge-yessica">🟢 YESSICA: {prod.get("stock_yessica",0)}</span> <span class="badge-apri004">🟡 APRI.004: {prod.get("stock_apri004",0)}</span> <span class="badge-apri001">🔴 APRI.001: {prod.get("stock_apri001",0)}</span>'
                    elif prod['tipo'] == 'UGREEN':
                        badge_stock = f'<span class="badge-ugreen">📦 UGREEN: {prod["stock_total"]}</span>'
                    else:
                        badge_stock = f'<span class="badge-otras">📦 DISPONIBLE: {prod["stock_total"]}</span>'
                    
                    st.markdown(f"""
                    <div style="background:white;border-radius:12px;padding:1rem;margin-bottom:1rem;border-left:5px solid {color_borde};">
                        <strong>📦 SKU: {prod['sku']}</strong><br>
                        <span style="font-size:0.9rem;">{prod['descripcion']}</span><br>
                        <strong style="color:#e67e22;">💰 {precio_str}</strong><br>
                        <div style="margin-top:8px;">{badge_stock}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if prod['tiene_stock'] and prod.get('precio', 0) > 0:
                        col_c, col_b = st.columns([1,3])
                        cant = col_c.number_input("Cant", min_value=1, max_value=prod['stock_total'], key=f"q_{prod['sku']}")
                        if col_b.button("➕ Agregar", key=f"add_{prod['sku']}"):
                            st.session_state.carrito.append({
                                'sku': prod['sku'], 'descripcion': prod['descripcion'], 'cantidad': cant,
                                'precio': prod['precio'], 'total': prod['precio'] * cant, 'tipo': prod['tipo']
                            })
                            st.rerun()
            else: st.info("No se encontraron resultados que coincidan con todas las palabras.")

with tab3:
    st.markdown("### 🛒 Cotizador Seguro")
    if not st.session_state.carrito: st.info("Carrito vacío")
    else:
        productos_mantener = []
        for idx, item in enumerate(st.session_state.carrito):
            c1, c2, c3, c4, c5 = st.columns([2, 4, 2, 2, 1])
            eliminar = False
            c1.write(f"**{item['sku']}**")
            c2.write(item['descripcion'][:50])
            nueva_cant = c3.number_input("Cant", min_value=0, value=item['cantidad'], key=f"c_{idx}_{item['sku']}")
            if nueva_cant != item['cantidad']:
                item['cantidad'], item['total'] = nueva_cant, item['precio'] * nueva_cant
            c4.write(f"S/ {item['total']:,.2f}")
            if c5.button("🗑️", key=f"d_{idx}_{item['sku']}"): eliminar = True
            
            if item['cantidad'] > 0 and not eliminar: productos_mantener.append(item)
            st.divider()
            
        if len(productos_mantener) != len(st.session_state.carrito) or any(i['cantidad'] != i.get('_last_q', i['cantidad']) for i in productos_mantener):
            st.session_state.carrito = productos_mantener
            st.rerun()
            
        st.markdown(f"### 💰 TOTAL: S/ {sum(i['total'] for i in st.session_state.carrito):,.2f}")
        cliente, ruc = st.text_input("Cliente"), st.text_input("RUC/DNI")
        if st.button("📥 Exportar Excel", type="primary") and cliente:
            st.download_button("Descargar", data=generar_excel(st.session_state.carrito, cliente, ruc), file_name=f"Cotizacion_{cliente}.xlsx")
