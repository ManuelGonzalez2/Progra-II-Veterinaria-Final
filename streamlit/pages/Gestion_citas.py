
import sys
import os
# La siguiente linea de codigo es un ajuste de ruta para que pueda encontrar la carpeta src
# Es la solución de emergencia para que los ficheros de pages reconozcan al motor.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import streamlit as st
import pandas as pd
from datetime import date
# Importamos Utils para usar la función de formatear nombre y buscar mejor
from src import Veterinaria, Utils 

# Aqui utilizamos el patron de singleton o memoria persistente, streamlit lo que hace es que cada vez que 
# un usuario hace clic, este se reinicia. Utilizamos la funcion st.session_state para que le diga a streamlit
# todo lo que pongamos se quede en su memoria. 
# st.session_state es como la caja de memoria
if "mi_clinica" not in st.session_state:
    st.session_state["mi_clinica"] = Veterinaria()

# Control de acceso
# Si no está loggeado, te dira que tienes que iniciar sesion
if "login_correcto" not in st.session_state or not st.session_state["login_correcto"]:
    st.warning("Debes iniciar sesión para acceder.")
    st.stop()

st.title("📅 Gestión de Citas")
# Recupera el objeto único de la clínica de la memoria persistente de Streamlit.
veterinaria = st.session_state["mi_clinica"]

# --- 1. Formulario para Crear Cita ---
st.subheader("Registrar Nueva Cita")
with st.form("form_cita"):
    st.write("Datos de la Mascota y el Dueño:")
    nombre_dueño = st.text_input("Nombre del Dueño", key="nombre_dueño_cita") 
    nombre_mascota = st.text_input("Nombre Mascota", key="mascota_cita")
    
    st.write("Detalles de la Cita:")
    col1, col2 = st.columns(2)
    with col1:
        fecha_cita = st.date_input("Fecha", value=date.today())
    with col2:
        hora_cita = st.text_input("Hora (HH:MM)", value="10:00")
        
    motivo = st.text_area("Motivo de la Cita")
    veterinario_responsable = st.selectbox("Veterinario Responsable", ["Dr. Rufino", "Dra. Ana", "Dr. Tomás"])
    
    #Ponemos un boton para subirlo
    submitted = st.form_submit_button("Programar Cita")
    
    # Aqui tenemos que meter toda la logica de la busqueda
    if submitted:
        cliente_encontrado = None
        
        # 1. Buscamos el cliente por nombre.
        # Utilizamos Utils.formatear_nombre para ser tolerantes a mayusculas y minusculas.
        for c in veterinaria.clientes:
            if Utils.formatear_nombre(c.nombre) == Utils.formatear_nombre(nombre_dueño):
                cliente_encontrado = c
                break

        if not cliente_encontrado:
            st.error("❌ Error: Cliente no encontrado por ese nombre. Revisa si está registrado.")
        else:
            # 2. Si encontramos al cliente, buscamos la mascota asociada a ese cliente.
            # Usamos next para buscar en la lista de mascotas del cliente.
            mascota_encontrada = next(
                (m for m in cliente_encontrado.mascotas if m.nombre.lower() == nombre_mascota.lower()), None 
            )
            
            if mascota_encontrada:
                # Ahora tenemos que crear la cita con la funcion de veterinaria
                veterinaria.crear_cita(fecha_cita, hora_cita, motivo, veterinario_responsable, mascota_encontrada)
                st.success(f"✅ Cita programada para {mascota_encontrada.nombre} (Dueño: {cliente_encontrado.nombre}) con el {veterinario_responsable}.")
            else:
                st.error(f"❌ Error: Mascota '{nombre_mascota}' no registrada para el cliente {cliente_encontrado.nombre}.")


# Creamos la tabla para poner los resultados de la cita
st.write("---")
st.subheader("Citas Programadas")

if veterinaria.citas:
    datos = {
        "Fecha": [c.fecha.strftime('%d/%m/%Y') for c in veterinaria.citas],
        "Hora": [c.hora for c in veterinaria.citas],
        "Mascota": [c.mascota.nombre for c in veterinaria.citas],
        "Dueño": [c.mascota.cliente.nombre for c in veterinaria.citas], 
        "Veterinario": [c.veterinario for c in veterinaria.citas],
        "Motivo": [c.motivo for c in veterinaria.citas]
    }
    df = pd.DataFrame(datos)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No hay citas programadas.")
