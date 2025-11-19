import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import streamlit as st
import pandas as pd
from src.veterinaria import Veterinaria

# --- Parche de Seguridad ---
if "mi_clinica" not in st.session_state:
    from src.veterinaria import Veterinaria
    st.session_state["mi_clinica"] = Veterinaria()
# ---------------------------

if "login_correcto" not in st.session_state or not st.session_state["login_correcto"]:
    st.warning("Debes iniciar sesión.")
    st.stop()

st.title("🐾 Listado de Pacientes (Mascotas)")
st.write("---")

veterinaria = st.session_state["mi_clinica"]

# Vamos a sacar una lista de todas las mascotas de todos los clientes
lista_mascotas = []

for cliente in veterinaria.clientes:
    for mascota in cliente.mascotas:
        lista_mascotas.append({
            "Nombre Mascota": mascota.nombre,
            "Especie": mascota.especie,
            "Raza": mascota.raza,
            "Fecha Nacimiento": mascota.fecha_nacimiento,
            "Dueño": cliente.nombre,  # Añadimos el dueño para saber de quién es
            "Contacto Dueño": cliente.telefono
        })

if not lista_mascotas:
    st.info("No hay mascotas registradas todavía.")
else:
    df = pd.DataFrame(lista_mascotas)
    st.dataframe(df, use_container_width=True)