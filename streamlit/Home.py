
import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.veterinaria import Veterinaria

st.set_page_config(page_title="Curae Veterinaria")

st.title("Curae Veterinaria - Inicio de Sesión")

if "mi_clinica" not in st.session_state:
    st.session_state["mi_clinica"] = Veterinaria()


if "login_correcto" not in st.session_state:
    st.session_state["login_correcto"] = False


if st.session_state["login_correcto"]:
    st.success("¡Bienvenido! Ya puedes navegar por el menú lateral.")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state["login_correcto"] = False
        st.rerun()

else:
    st.write("Por favor, introduzca sus credenciales para acceder.")
    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Iniciar Sesión"):
        # Las credenciales son : ADMIN / Curae1234
        if usuario == "ADMIN" and password == "Curae1234":
            st.session_state["login_correcto"] = True
            st.success("¡Login correcto! Accediendo...")
            st.balloons()
            st.rerun() # Recarga para mostrar el menú
        else:
            st.error("El usuario o la contraseña son incorrectos")