import sys
import os
# La siguiente linea de codigo es un ajuste de ruta para que pueda encontrar la carpeta src
# Es la solución de emergencia para que los ficheros de pages reconozcan al motor.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import streamlit as st
import pandas as pd
from src.veterinaria import Veterinaria

# Aqui utilizamos el patron de singleton o memoria persistente, streamlit lo que hace es que cada vez que 
# un usuario hace clic, este se reinicia. Utilizamos la funcion st.session_state para que le diga a streamlit
# todo lo que pongamos se quede en su memoria.
if "mi_clinica" not in st.session_state:
    st.session_state["mi_clinica"] = Veterinaria()

# Si no estás logueado, te manda a la página principal
if "login_correcto" not in st.session_state or not st.session_state["login_correcto"]:
    st.warning("Debes iniciar sesión.")
    st.stop()

st.title("🐾 Listado de Pacientes (Mascotas)")
st.write("---")

veterinaria = st.session_state["mi_clinica"]


lista_mascotas = []
# Mascotas ss una lista anidada de clientes (cada cliente tiene su propia lista de mascotas).
# Tenemos que usar dos bucles for para sacar todas las mascotas individualmente 
# y que cada animal tenga su propia fila en la tabla.
for cliente in veterinaria.clientes:
    for mascota in cliente.mascotas:
        lista_mascotas.append({
            "Nombre Mascota": mascota.nombre,
            "Especie": mascota.especie,
            "Raza": mascota.raza,
            "Fecha Nacimiento": mascota.fecha_nacimiento,
            "Dueño": cliente.nombre,  
            "Contacto Dueño": cliente.telefono
        })

if not lista_mascotas:
    st.info("No hay mascotas registradas todavía.")
else:
    df = pd.DataFrame(lista_mascotas)
    st.dataframe(df, use_container_width=True)
