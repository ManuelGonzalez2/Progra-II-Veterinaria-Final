import sys
import os

# Tenemos que calcular las rutas exactas para que python no se lie
# La carpeta donde está db_utils (la carpeta 'streamlit')
current_dir = os.path.dirname(__file__)
streamlit_folder = os.path.abspath(os.path.join(current_dir, ".."))
# La raíz del proyecto (donde está 'src')
root_project = os.path.abspath(os.path.join(current_dir, "../.."))

# 2. Las añadimos al sistema si no están ya
if streamlit_folder not in sys.path:
    sys.path.insert(0, streamlit_folder)
if root_project not in sys.path:
    sys.path.insert(0, root_project)

import streamlit as st
from datetime import date
import re
from db_utils import run_query, create_tables 
from src.utils import Utils

st.set_page_config(page_title="Registrar Cliente y Mascota", page_icon="👤", layout="wide")

def app():
    # Nos aseguramos de que la tabla exista con los nuevos campos
    create_tables()

    st.title("👤 Registrar Cliente y Mascota")
    st.caption("Introduce los datos para crear un nuevo expediente en la base de datos.")

    with st.form("registro_completo", border=True):
        st.subheader("Datos de Registro")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("#### 1. Datos del Dueño (Cliente)")
            nombre_propietario = st.text_input("Nombre Completo Dueño", max_chars=50)
            telefono = st.text_input("Teléfono", max_chars=15)
            email = st.text_input("Email")
        
        with col2:
            st.write("#### 2. Datos de la Mascota")
            nombre_mascota = st.text_input("Nombre de la Mascota")
            especie = st.selectbox("Especie", ["Perro", "Gato", "Ave", "Conejo", "Reptil", "Otro"])
            raza = st.text_input("Raza")
            fecha_nac = st.date_input("Fecha de Nacimiento", value=date.today())
        
        st.write("---")
        
        # Botón de guardar
        submitted = st.form_submit_button("✅ Registrar en Base de Datos", type="primary")

        if submitted:
            #Validaciones
            errores = []
            if not nombre_propietario: errores.append("Falta el nombre del dueño.")
            if not nombre_mascota: errores.append("Falta el nombre de la mascota.")
            # Validación de mail con utils
            if email and not Utils.validar_email(email): 
                errores.append("El formato del email no es válido.")

            if errores:
                for e in errores:
                    st.error(f"ERROR {e}")
            else:
                try:
                    query = """
                        INSERT INTO pacientes 
                        (nombre, especie, raza, fecha_nacimiento, propietario, telefono, email) 
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """
                    params = (
                        nombre_mascota, 
                        especie, 
                        raza, 
                        str(fecha_nac), 
                        nombre_propietario, 
                        telefono, 
                        email
                    )
                    
                    run_query(query, params)
                    
                    st.success(f"✅ ¡Éxito! Expediente creado para **{nombre_mascota}** (Dueño: {nombre_propietario}).")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"Ocurrió un error al guardar en la base de datos: {e}")

if __name__ == "__main__":
    app()