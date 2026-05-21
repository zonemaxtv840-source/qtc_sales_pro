# ui/styles.py
import streamlit as st

def apply_custom_styles():
    st.markdown("""
    <style>
        /* ========== FONDO DE PÁGINA ========== */
        .stApp {
            background: linear-gradient(135deg, #0d47a1 0%, #1565c0 50%, #1e88e5 100%);
        }
        
        /* ========== SIDEBAR ========== */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f8a35e 0%, #e87a2d 50%, #d45a1a 100%);
            border-right: 1px solid #ffcc80;
        }
        
        [data-testid="stSidebar"] * {
            color: #ffffff !important;
        }
        
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] .stMarkdown {
            color: #ffffff !important;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        }
        
        /* ========== TEXTOS GENERALES ========== */
        .stMarkdown, .stText, .stNumberInput label, .stSelectbox label,
        .stRadio label, .stTextInput label {
            color: #ffffff !important;
        }
        
        h1, h2, h3, h4, h5, h6,
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            color: #ffffff !important;
        }
        
        /* ========== CARDS MEJORADAS ========== */
        /* Card base */
        .card-result {
            background: white;
            border-radius: 12px;
            padding: 0.75rem 1rem;
            margin-bottom: 0.75rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: all 0.2s ease;
            border-left: 4px solid;
        }
        
        .card-result:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        /* Header de card */
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        }
        
        .card-sku {
            font-family: 'Courier New', monospace;
            font-weight: bold;
            font-size: 0.9rem;
            background: #f0f0f0;
            padding: 2px 8px;
            border-radius: 6px;
            color: #1565c0 !important;
        }
        
        .card-badge {
            padding: 2px 10px;
            border-radius: 20px;
            font-size: 0.65rem;
            font-weight: bold;
            color: white !important;
        }
        
        .badge-success { background: #4CAF50; }
        .badge-warning { background: #FF9800; }
        .badge-danger { background: #f44336; }
        .badge-info { background: #2196F3; }
        .badge-stock-yessica { background: #4CAF50; }
        .badge-stock-apri004 { background: #FF9800; }
        .badge-stock-apri001 { background: #f44336; }
        .badge-ugreen { background: #00BCD4; }
        
        /* Contenido de card */
        .card-desc {
            font-size: 0.8rem;
            color: #555 !important;
            margin-bottom: 0.5rem;
            line-height: 1.3;
        }
        
        .card-details {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            font-size: 0.75rem;
            color: #666 !important;
            margin-top: 0.5rem;
            padding-top: 0.5rem;
            border-top: 1px solid #eee;
        }
        
        .card-details span {
            color: #666 !important;
        }
        
        .card-details strong {
            color: #1565c0 !important;
        }
        
        .card-status {
            margin-top: 0.5rem;
            font-size: 0.7rem;
            padding: 4px 8px;
            background: #f5f5f5;
            border-radius: 8px;
            color: #555 !important;
        }
        
        /* ========== TARJETA DE RESUMEN ========== */
        .summary-card {
            background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
            border-radius: 12px;
            padding: 1rem;
            margin: 1rem 0;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        
        .summary-card h4 {
            color: white !important;
            margin: 0 0 0.5rem 0;
            font-size: 0.9rem;
        }
        
        .summary-card .number {
            font-size: 2rem;
            font-weight: bold;
            color: #ff9800 !important;
        }
        
        /* ========== TABLA DE RESULTADOS ========== */
        .dataframe-container {
            background: white;
            border-radius: 12px;
            padding: 0.5rem;
            overflow-x: auto;
        }
        
        .dataframe-container table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .dataframe-container th {
            background: #1565c0;
            color: white !important;
            padding: 8px;
            font-size: 0.75rem;
        }
        
        .dataframe-container td {
            color: #333 !important;
            padding: 6px 8px;
            font-size: 0.7rem;
            border-bottom: 1px solid #eee;
        }
        
        /* ========== BOTONES ========== */
        .stButton > button {
            border-radius: 8px !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }
        
        /* ========== INPUTS ========== */
        .stTextInput input, .stTextArea textarea, .stNumberInput input {
            border-radius: 8px !important;
            border: 1px solid #ddd !important;
        }
        
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: #1565c0 !important;
            box-shadow: 0 0 0 2px rgba(21,101,192,0.2) !important;
        }
        
        /* ========== TABS ========== */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 6px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 500;
        }
        
        .stTabs [aria-selected="true"] {
            background: white !important;
            color: #1565c0 !important;
        }
        
        /* ========== EXPANDER ========== */
        .streamlit-expanderHeader {
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
            color: white !important;
        }
        
        .streamlit-expanderContent {
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
        }
        
        /* ========== METRIC ========== */
        [data-testid="stMetricValue"] {
            color: #ff9800 !important;
            font-size: 1.5rem !important;
        }
        
        [data-testid="stMetricLabel"] {
            color: white !important;
        }
        
        /* ========== FOOTER ========== */
        .footer {
            text-align: center;
            padding: 1rem;
            color: rgba(255,255,255,0.6);
            font-size: 0.7rem;
            border-top: 1px solid rgba(255,255,255,0.1);
            margin-top: 2rem;
        }
        
        /* ========== ALERTAS ========== */
        div[data-testid="stAlert"] {
            border-radius: 10px !important;
        }
        
        div[data-testid="stAlert"][data-kind="success"] {
            background: #2e7d32 !important;
        }
        
        div[data-testid="stAlert"][data-kind="warning"] {
            background: #f9a825 !important;
        }
        
        div[data-testid="stAlert"][data-kind="error"] {
            background: #d32f2f !important;
        }
        
        /* ========== PROGRESS ========== */
        .stProgress > div > div {
            background-color: #ff9800 !important;
        }
        
        /* ========== SCROLLBAR ========== */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 3px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 3px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
    </style>
    """, unsafe_allow_html=True)
