import streamlit as st
from utils.constants import COLORES_BADGES, ALMACENES

def construir_badge_stock(stock_dict):
    """HTML para badges de stock"""
    badges = []
    for almacen in ["YESSICA", "APRI.004", "APRI.001"]:
        cantidad = stock_dict.get(almacen, 0)
        color = COLORES_BADGES.get(almacen, "gris")
        if cantidad > 0:
            badges.append(f'<span style="background:{color}; padding:4px 12px; border-radius:20px; font-size:12px; margin:2px; display:inline-block;">📦 {almacen}: {cantidad}</span>')
        else:
            badges.append(f'<span style="background:#95a5a6; padding:4px 12px; border-radius:20px; font-size:12px; margin:2px; display:inline-block; opacity:0.5;">❌ {almacen}: 0</span>')
    return " ".join(badges)

def crear_tarjeta_producto(producto, inventario, key_suffix=""):
    """Crea card de producto profesional"""
    badges_html = construir_badge_stock(inventario["stock"])
    precio = inventario["precio"] or 0
    precio_texto = f"S/ {precio:,.2f}" if precio else "Consultar precio"
    
    card_html = f"""
    <div style="background:white; border-radius:16px; padding:20px; margin:12px 0; box-shadow:0 2px 8px rgba(0,0,0,0.05); border:1px solid #eef2f6;">
        <div style="display:flex; justify-content:space-between; align-items:start;">
            <div style="flex:1;">
                <h4 style="color:#1a1a2e; margin:0 0 8px 0;">{producto.get('Descripcion', 'Sin descripción')}</h4>
                <p style="color:#7f8c8d; font-size:13px; margin:0 0 12px 0;">
                    <strong>SKU:</strong> {inventario['sku']}
                </p>
                <div style="margin:12px 0;">
                    {badges_html}
                </div>
            </div>
            <div style="text-align:right; min-width:150px;">
                <div style="font-size:24px; font-weight:bold; color:#e67e22;">
                    {precio_texto}
                </div>
            </div>
        </div>
    </div>
    """
    return card_html

def aplicar_estilos_globales():
    """CSS global de la aplicación"""
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .main > div {
        background: transparent;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255,255,255,0.1);
        padding: 8px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 20px;
        background: rgba(255,255,255,0.2);
        color: white;
    }
    .stTabs [aria-selected="true"] {
        background: white;
        color: #1a1a2e;
    }
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ff9a9e 0%, #fecfef 100%);
    }
    </style>
    """, unsafe_allow_html=True)
