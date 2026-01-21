# src/app.py

import streamlit as st

from src.core.config import load_settings
from src.core.auth import authenticate, set_user_session, get_user_session, logout
from src.ui.styles import apply_global_styles
from src.ui.pages import pedidos_page
from src.data.sheets_client import debug_sa_email
st.sidebar.caption(f"Service Account: {debug_sa_email()}")



def login_screen(settings):
    st.title("Rotisería – Panel de pedidos")
    st.caption("Login requerido (admin / owner)")

    with st.form("login_form"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Ingresar")

    if submitted:
        user = authenticate(settings, username, password)
        if user:
            set_user_session(user)
            st.success("Login correcto.")
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos.")


def main():
    st.set_page_config(page_title="Rotisería - Pedidos", layout="wide")
    apply_global_styles()

    try:
        settings = load_settings()
    except Exception as e:
        st.error(f"Configuración inválida: {e}")
        st.stop()

    user = get_user_session()
    if not user:
        login_screen(settings)
        st.stop()

    st.sidebar.write(f"Usuario: {user['username']}")
    st.sidebar.write(f"Rol: {user['role']}")
    if st.sidebar.button("Cerrar sesión"):
        logout()
        st.rerun()

    pedidos_page(
        spreadsheet_id=settings.app.spreadsheet_id,
        worksheet_name=settings.app.worksheet_name,
        role=user["role"],
    )


if __name__ == "__main__":
    main()
