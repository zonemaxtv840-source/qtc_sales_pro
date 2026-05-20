# ui/components.py
import streamlit as st

def mostrar_header(user_name: str, user_role: str):
    col1, col2, col3 = st.columns([1, 5, 2])
    with col1:
        st.markdown("**QTC**", unsafe_allow_html=True)
    with col2:
        st.markdown("# QTC Smart Sales Pro")
        st.caption("Sistema Profesional de Cotización")
    with col3:
        role_badge = {"ADMIN": "🔧", "KAM": "⭐", "VENDEDOR": "🛒", "INVITADO": "👤"}
        badge = role_badge.get(user_role, "👤")
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.1); padding: 0.5rem 1rem; border-radius: 12px; text-align: right;">
            <span>{badge} {user_name}</span><br>
            <span style="font-size: 0.7rem;">{user_role}</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚪 Cerrar Sesión", key="logout"):
            return False
    return True
