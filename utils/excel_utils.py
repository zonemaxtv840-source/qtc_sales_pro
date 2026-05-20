# utils/excel_utils.py
import pandas as pd
import streamlit as st

def corregir_numero(valor) -> float:
    if pd.isna(valor) or str(valor).strip() in ["", "0"]:
        return 0.0
    try:
        return float(valor)
    except:
        return 0.0
