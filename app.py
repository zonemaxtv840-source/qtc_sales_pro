# app.py - QTC Smart Sales Pro v5.0

import streamlit as st
import pandas as pd
import re
import io
from datetime import datetime
from difflib import SequenceMatcher

st.set_page_config(
    page_title="QTC Smart Sales Pro",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS
# ============================================

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0d47a1 0%, #1565c0 50%, #1e88e5 100%); }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #f8a35e 0%, #e87a2d 50%, #d45a1a 100%); }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .badge-yessica { background: #4CAF50; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; display: inline-block; margin: 2px; }
    .badge-apri004 { background: #FF9800; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; display: inline-block; margin: 2px; }
    .badge-apri001 { background: #f44336; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; display: inline-block; margin: 2px; }
    .footer { text-align: center; padding: 1rem; color: rgba(255,255,255,0.7); font-size: 0.7rem; margin-top: 2rem; }
    div[style*="background:white"] * { color: #1a1a2e !important; }
</style>
""", unsafe_allow_html=True)

# ============================================
# FUNCIONES
# ============================================

def corregir_numero(valor) -> float:
    if pd.isna(valor) or str(valor).strip() in ["", "0", "0.0", "-"]:
        return 0.0
    s = str(valor).upper().replace('S/', '').replace('$', '').replace(' ', '').strip()
    if ',' in s and '.' in s:
        s = s.replace(',', '')
    elif ',' in s:
        partes = s.split(',')
        if len(partes[-1]) <= 2:
            s = s.replace(',', '.')
        else:
            s = s.replace(',', '')
    s = re.sub(r'[^\d.]', '', s)
    try:
        return float(s)
    except:
        return 0.0

def limpiar_cabeceras(df: pd.DataFrame) -> pd.DataFrame:
    for i in range(min(20, len(df))):
        fila = [str(x).upper() for x in df.iloc[i].values]
        if any(h in item for h in ['SKU', 'COD', 'SAP', 'NUMERO', 'ARTICULO'] for item in fila):
            df.columns = [str(c).strip() for c in df.iloc[i]]
            return df.iloc[i+1:].reset_index(drop=True)
    return df

def detectar_columna_sku(df: pd.DataFrame) -> str:
    posibles = ['SKU', 'COD', 'SAP', 'NUMERO', 'ARTICULO', 'CODIGO']
    for col in df.columns:
        col_upper = str(col).upper()
        for posible in posibles:
            if posible.upper() in col_upper:
                return col
    return df.columns[0]

def cargar_archivo(uploaded_file):
    if uploaded_file is None:
        return None
    nombre = uploaded_file.name.lower()
    try:
        if nombre.endswith('.csv'):
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            except:
                df = pd.read_csv(uploaded_file, encoding='latin-1')
        else:
            df = pd.read_excel(uploaded_file)
        return limpiar_cabeceras(df)
    except Exception as e:
        st.error(f"Error cargando {nombre}: {str(e)[:80]}")
        return None

# ============================================
# INICIALIZACIÓN DE SESIÓN
# ============================================

if 'auth' not in st.session_state:
    st.session_state.auth = False
if 'modo' not in st.session_state:
    st.session_state.modo = "XIAOMI"
if 'precio_key' not in st.session_state:
    st.session_state.precio_key = "P. VIP"
if 'catalogos' not in st.session_state:
    st.session_state.catalogos = []
if 'stocks' not in st.session_state:
    st.session_state.stocks = []
if 'carrito' not in st.session_state:
    st.session_state.carrito = []
if 'ugreen_catalogo' not in st.session_state:
    st.session_state.ugreen_catalogo = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None

# ============================================
# LOGIN
# ============================================

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div style="background:rgba(255,255,255,0.95);border-radius:20px;padding:2rem;">', unsafe_allow_html=True)
        
        try:
            st.image("logo.png", width=100)
        except:
            st.markdown("<h1 style='color:#e94560;text-align:center;'>QTC</h1>", unsafe_allow_html=True)
        
        st.markdown("<h2 style='color:#1a1a2e;text-align:center;'>QTC Smart Sales Pro</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#666;text-align:center;'>Sistema Profesional de Cotización</p>", unsafe_allow_html=True)
        
        usuario = st.text_input("👤 Usuario", placeholder="admin / kimberly / vendedor")
        password = st.text_input("🔒 Contraseña", type="password")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🚀 Ingresar", use_container_width=True):
                credenciales = {
                    "admin": {"password": "qtc2026", "rol": "ADMIN", "nombre": "Administrador"},
                    "kimberly": {"password": "kam2026", "rol": "KAM", "nombre": "Kimberly"},
                    "vendedor": {"password": "ventas2026", "rol": "VENDEDOR", "nombre": "Vendedor"}
                }
                if usuario in credenciales and password == credenciales[usuario]["password"]:
                    st.session_state.auth = True
                    st.session_state.user_role = credenciales[usuario]["rol"]
                    st.session_state.user_name = credenciales[usuario]["nombre"]
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas")
        with col_btn2:
            if st.button("👤 Invitado", use_container_width=True):
                st.session_state.auth = True
                st.session_state.user_role = "INVITADO"
                st.session_state.user_name = "Invitado"
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.stop()

# ============================================
# HEADER
# ============================================

col1, col2, col3 = st.columns([1, 5, 2])
with col1:
    try:
        st.image("logo.png", width=60)
    except:
        st.markdown("**QTC**", unsafe_allow_html=True)
with col2:
    st.markdown("# QTC Smart Sales Pro")
    st.caption("Sistema Profesional de Cotización | Soporte XIAOMI · UGREEN")
with col3:
    role_badge = {"ADMIN": "🔧", "KAM": "⭐", "VENDEDOR": "🛒", "INVITADO": "👤"}
    badge = role_badge.get(st.session_state.user_role, "👤")
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.1); padding: 0.5rem 1rem; border-radius: 12px; text-align: right;">
        <span>{badge} {st.session_state.user_name}</span><br>
        <span style="font-size: 0.7rem;">{st.session_state.user_role}</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🚪 Cerrar Sesión", key="logout"):
        st.session_state.auth = False
        st.session_state.carrito = []
        st.rerun()

st.markdown("---")

# ============================================
# SIDEBAR
# ============================================

with st.sidebar:
    st.markdown("### 🎯 Configuración")
    
    marca_seleccionada = st.radio("📌 Marca / Modo", ["XIAOMI", "UGREEN"], index=0)
    st.session_state.modo = marca_seleccionada
    
    st.markdown("---")
    
    precio_opcion = st.radio("💰 Nivel de precio", ["P. VIP", "P. BOX", "P. IR"], index=0)
    st.session_state.precio_key = precio_opcion
    
    st.markdown("---")
    
    st.markdown("### 📂 Archivos")
    
    if marca_seleccionada == "XIAOMI":
        archivos_cat = st.file_uploader("📚 Catálogos", type=['xlsx', 'xls', 'csv'], accept_multiple_files=True, key="cat_upload")
        archivos_stock = st.file_uploader("📦 Stock", type=['xlsx', 'xls'], accept_multiple_files=True, key="stock_upload")
        
        if archivos_cat:
            st.session_state.catalogos = []
            for archivo in archivos_cat:
                df = cargar_archivo(archivo)
                if df is not None:
                    st.session_state.catalogos.append({
                        'nombre': archivo.name,
                        'df': df,
                        'col_sku': detectar_columna_sku(df),
                        'col_desc': None,
                        'precios': {}
                    })
                    st.success(f"✅ {archivo.name[:30]}")
        
        if archivos_stock:
            st.session_state.stocks = []
            for archivo in archivos_stock:
                try:
                    xls = pd.ExcelFile(archivo)
                    for hoja in xls.sheet_names:
                        if any(h in hoja.upper() for h in ['APRI', 'YESSICA']):
                            df = pd.read_excel(archivo, sheet_name=hoja)
                            df = limpiar_cabeceras(df)
                            st.session_state.stocks.append({
                                'nombre': f"{archivo.name} [{hoja}]",
                                'df': df,
                                'col_sku': detectar_columna_sku(df),
                                'col_cant': None,
                                'hoja': hoja
                            })
                            st.success(f"✅ Stock {hoja}")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    st.markdown("---")
    
    if st.session_state.carrito:
        total = sum(item.get('total', 0) for item in st.session_state.carrito)
        st.metric("Total Carrito", f"S/ {total:,.2f}")
        if st.button("🧹 Limpiar carrito", use_container_width=True):
            st.session_state.carrito = []
            st.rerun()

# ============================================
# TABS
# ============================================

tab1, tab2, tab3 = st.tabs(["📦 MODO MASIVO", "🔍 BÚSQUEDA", "🛒 CARRITO"])

with tab1:
    st.markdown("### 📦 Modo Masivo")
    
    if st.session_state.catalogos and st.session_state.stocks:
        st.success(f"✅ Sistema listo - {len(st.session_state.catalogos)} catálogos, {len(st.session_state.stocks)} stocks cargados")
        
        texto_bulk = st.text_area("Ingresa SKUs:", height=150, placeholder="RN0200065BK8:5\nCN0200047BK8:10")
        
        if st.button("Procesar lista", type="primary"):
            if texto_bulk:
                st.info("Procesando...")
            else:
                st.warning("Ingresa al menos un SKU")
    else:
        st.info("📌 Carga archivos de catálogo y stock en el panel izquierdo")

with tab2:
    st.markdown("### 🔍 Búsqueda Inteligente")
    
    busqueda = st.text_input("", placeholder="Ej: RN0200065BK8 o Type-C Earphones")
    
    if busqueda and len(busqueda) >= 2:
        if st.session_state.catalogos and st.session_state.stocks:
            st.info(f"🔍 Buscando: {busqueda}")
        else:
            st.warning("⚠️ Carga archivos de catálogo y stock primero")

with tab3:
    st.markdown("### 🛒 Carrito")
    
    if not st.session_state.carrito:
        st.info("No hay productos en el carrito")
    else:
        for idx, item in enumerate(st.session_state.carrito):
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.write(item.get('sku', 'N/A'))
            with col2:
                st.write(f"{item.get('cantidad', 0)} x S/ {item.get('precio', 0):.2f}")
            with col3:
                if st.button("🗑️", key=f"del_{idx}"):
                    st.session_state.carrito.pop(idx)
                    st.rerun()
        
        total_general = sum(item.get('total', 0) for item in st.session_state.carrito)
        st.markdown(f"### TOTAL: S/ {total_general:,.2f}")

# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.markdown(f'<div class="footer">⚡ QTC Smart Sales Pro v5.0 | Modo: {st.session_state.modo}</div>', unsafe_allow_html=True)
