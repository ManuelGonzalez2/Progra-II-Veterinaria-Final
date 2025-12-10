import sys
import os
# La siguiente linea de codigo es un ajuste de ruta para que pueda encontrar la carpeta src
# Es la solución de emergencia para que los ficheros de pages reconozcan al motor.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import streamlit as st
import pandas as pd
from src import Veterinaria 

# Si no estás logueado, te manda a la página principal
if "login_correcto" not in st.session_state or not st.session_state["login_correcto"]:
    st.warning("Debes iniciar sesión para acceder.")
    st.stop() 

st.title("📋 Clientes Registrados")
st.write("---")

# Aqui utilizamos el patron de singleton o memoria persistente, streamlit lo que hace es que cada vez que 
# un usuario hace clic, este se reinicia. Utilizamos la funcion st.session_state para que le diga a streamlit
# todo lo que pongamos se quede en su memoria.
if "mi_clinica" not in st.session_state:
    st.session_state["mi_clinica"] = Veterinaria()


veterinaria = st.session_state["mi_clinica"]

if not veterinaria.clientes:
    st.info("Aún no hay clientes registrados en el sistema.")
else:
    datos = {
        "Nombre": [c.nombre for c in veterinaria.clientes],
        "Teléfono": [c.telefono for c in veterinaria.clientes],
        "Email": [c.email for c in veterinaria.clientes],
        "Mascotas": [len(c.mascotas) for c in veterinaria.clientes]
    }
    df = pd.DataFrame(datos)
    st.dataframe(df, use_container_width=True)

st.write("---")
st.subheader(" Dar de Baja un Cliente")

with st.form("form_eliminar"):
    email_eliminar = st.text_input("Email del Cliente a Eliminar (Eliminará todas sus mascotas)")
    confirm_button = st.form_submit_button("Eliminar Cliente DEFINITIVAMENTE")
    
    if confirm_button:
        if email_eliminar:
            if veterinaria.eliminar_cliente(email_eliminar):
                st.session_state["mensaje_status"] = "✅ Cliente y mascotas eliminados con éxito."
            else:
                st.session_state["mensaje_status"] = "❌ Error: No se encontró ningún cliente con ese email."
            st.rerun()
        else:
            st.error("Por favor, introduzca el email del cliente.")
