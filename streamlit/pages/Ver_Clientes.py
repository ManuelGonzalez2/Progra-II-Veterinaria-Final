import sys
import os

# Truco para que Python encuentre la carpeta 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import streamlit as st
import pandas as pd
from src import Veterinaria # Ahora sí debería encontrarlo 

# Si no estás logueado, te manda a la página principal
if "login_correcto" not in st.session_state or not st.session_state["login_correcto"]:
    st.warning("Debes iniciar sesión para acceder.")
    st.stop() # Detiene la ejecución

st.title("📋 Clientes Registrados")
st.write("---")

# --- INICIO DEL PARCHE ---
if "mi_clinica" not in st.session_state:
    # Si la memoria está vacía, importamos y creamos la clínica aquí mismo
    from src.veterinaria import Veterinaria
    st.session_state["mi_clinica"] = Veterinaria()
# --- FIN DEL PARCHE ---

# Accedemos al motor (la clase Veterinaria)
veterinaria = st.session_state["mi_clinica"]

if not veterinaria.clientes:
    st.info("Aún no hay clientes registrados en el sistema.")
else:
    # Creamos un DataFrame (Req. 21) para mostrar los datos
    datos = {
        "Nombre": [c.nombre for c in veterinaria.clientes],
        "Teléfono": [c.telefono for c in veterinaria.clientes],
        "Email": [c.email for c in veterinaria.clientes],
        "Mascotas": [len(c.mascotas) for c in veterinaria.clientes]
    }
    df = pd.DataFrame(datos)
    st.dataframe(df, use_container_width=True)
