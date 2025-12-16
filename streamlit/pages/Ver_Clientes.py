import sys
import os
# La siguiente linea de codigo es un ajuste de ruta para que pueda encontrar la carpeta src
# Es la solución de emergencia para que los ficheros de pages reconozcan al motor.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import streamlit as st
import pandas as pd
from src import Veterinaria 

# --- Configuración de la Página de Streamlit ---
st.set_page_config(page_title="Ver Clientes", page_icon="📋", layout="wide")

# Inicialización de la clase Veterinaria (Singleton)
if "mi_clinica" not in st.session_state:
    st.session_state["mi_clinica"] = Veterinaria()

# Control de acceso
if "login_correcto" not in st.session_state or not st.session_state["login_correcto"]:
    st.warning("🔒 Debes iniciar sesión para acceder al registro de clientes.")
    st.stop() 

st.title("🧑‍💻 Clientes Registrados")
st.caption("Listado completo de dueños en el sistema.")

veterinaria = st.session_state["mi_clinica"]

# --- 1. Mostrar Mensaje de Status (si hay uno tras un RERUN) ---
if "mensaje_status" in st.session_state:
    if st.session_state["mensaje_status"].startswith("✅"):
        st.success(st.session_state["mensaje_status"])
    else:
        st.error(st.session_state["mensaje_status"])
    # Limpiar mensaje después de mostrarlo
    del st.session_state["mensaje_status"]
    
# --- 2. Tabla de Clientes ---
st.subheader("BBDD de Dueños Activos")

if not veterinaria.clientes:
    st.info("ℹ️ Aún no hay clientes registrados en el sistema.")
else:
    datos = {
        # Incluimos el ID de la base de datos (clave primaria)
        "ID": [c.id[:8] + "..." for c in veterinaria.clientes], 
        "Nombre": [c.nombre for c in veterinaria.clientes],
        "Teléfono": [c.telefono for c in veterinaria.clientes],
        "Email": [c.email for c in veterinaria.clientes],
        "Mascotas": [len(c.mascotas) for c in veterinaria.clientes]
    }
    df = pd.DataFrame(datos)
    
    st.dataframe(
        df, 
        use_container_width=True,
        # Ocultamos el ID para que la tabla sea más limpia, pero es importante tenerlo
        column_config={"ID": st.column_config.TextColumn("ID", disabled=True)}, 
        hide_index=True
    )

st.divider()

# --- 3. Dar de Baja un Cliente (Mejora estética y confirmación) ---
st.subheader("❌ Dar de Baja un Cliente")
st.warning("⚠️ Esta acción es irreversible y eliminará **TODAS** las mascotas y citas asociadas (DELETE CASCADE).")

with st.form("form_eliminar", border=True):
    col_input, col_button = st.columns([3, 1])
    
    with col_input:
        email_eliminar = st.text_input("Email del Cliente a Eliminar", key="email_baja")
    
    with col_button:
        # Espacio para alinear el botón
        st.write(" ") 
        confirm_button = st.form_submit_button("Eliminar Cliente DEFINITIVAMENTE", type="primary")
    
    if confirm_button:
        if email_eliminar:
            # Usamos el mismo mensaje de status que se mostrará arriba tras el rerun
            if veterinaria.eliminar_cliente(email_eliminar):
                st.session_state["mensaje_status"] = "✅ Cliente y mascotas eliminados con éxito."
            else:
                st.session_state["mensaje_status"] = "❌ Error: No se encontró ningún cliente con ese email."
            st.rerun() # Actualiza la página para mostrar el nuevo listado y el mensaje
        else:
            st.error("Por favor, introduzca el email del cliente.")