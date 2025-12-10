import sys
import os
# La siguiente linea de codigo es un ajuste de ruta para que pueda encontrar la carpeta src
# Es la solución de emergencia para que los ficheros de pages reconozcan al motor.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import streamlit as st
from src.veterinaria import Veterinaria
from src.utils import Utils
from datetime import date

# Aqui utilizamos el patron de singleton o memoria persistente, streamlit lo que hace es que cada vez que 
# un usuario hace clic, este se reinicia. Utilizamos la funcion st.session_state para que le diga a streamlit
# todo lo que pongamos se quede en su memoria.
if "mi_clinica" not in st.session_state:
    st.session_state["mi_clinica"] = Veterinaria()


# Seguridad: Si no está logueado, detener la ejecución
if "login_correcto" not in st.session_state or not st.session_state["login_correcto"]:
    st.warning("Debes iniciar sesión para acceder.")
    st.stop()

st.title("👤 Registrar Cliente y Mascota")
st.write("---")

veterinaria = st.session_state["mi_clinica"]

with st.form("registro_completo"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Datos del Dueño")
        nombre = st.text_input("Nombre del Cliente", max_chars=50)
        telefono = st.text_input("Teléfono", max_chars=15)
        email = st.text_input("Email")
    
    with col2:
        st.subheader("2. Datos de la Mascota")
        nombre_mascota = st.text_input("Nombre de la Mascota")
        # Opciones predefinidas para ir más rápido en el vídeo
        especie = st.selectbox("Especie", ["Perro", "Gato", "Ave", "Conejo", "Otro"])
        raza = st.text_input("Raza")
        # Fecha de nacimiento (por defecto hoy)
        fecha_nac = st.date_input("Fecha de Nacimiento", value=date.today())
    
    # Botón de envío
    submitted = st.form_submit_button("Registrar Todo")

    if submitted:
        # Aqui ponemos las validaciones
        if not nombre or not email or not nombre_mascota:
             st.error("❌ Faltan campos obligatorios (Nombre, Email o Nombre Mascota).")
        #Aqui ponemos la funcion de utils de que el mail tiene que tener @ y .
        elif not Utils.validar_email(email):
            st.error("❌ El email no es válido.")
        else:
            # 2. Registrar Cliente
            nombre_formateado = Utils.formatear_nombre(nombre)
            cliente_creado = veterinaria.registrar_cliente(nombre_formateado, telefono, email)
            
            if cliente_creado:
                # 3. Registrar Mascota (asociada al email del cliente)
                veterinaria.registrar_mascota(
                    email, 
                    Utils.formatear_nombre(nombre_mascota), 
                    especie, 
                    raza, 
                    fecha_nac
                )
                
                st.success(f"✅ ¡Éxito! Se ha registrado a {nombre_formateado} y a su mascota {nombre_mascota}.")
            else:
                st.error("Hubo un error al registrar el cliente.")