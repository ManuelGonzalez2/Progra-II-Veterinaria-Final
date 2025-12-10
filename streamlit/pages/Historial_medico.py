import sys
import os
# La siguiente linea de codigo es un ajuste de ruta para que pueda encontrar la carpeta src
# Es la solución de emergencia para que los ficheros de pages reconozcan al motor.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import streamlit as st
from src import Veterinaria, Utils
from datetime import date
import pandas as pd

# Aqui utilizamos el patron de singleton o memoria persistente, streamlit lo que hace es que cada vez que 
# un usuario hace clic, este se reinicia. Utilizamos la funcion st.session_state para que le diga a streamlit
# todo lo que pongamos se quede en su memoria.
if "mi_clinica" not in st.session_state:
    st.session_state["mi_clinica"] = Veterinaria()

# Seguridad: Si no está logueado, detener la ejecución
if "login_correcto" not in st.session_state or not st.session_state["login_correcto"]:
    st.warning("Debes iniciar sesión para acceder al historial.")
    st.stop()

st.title("🩺 Historial Médico y Tratamientos")
veterinaria = st.session_state["mi_clinica"]

# --- 1. Búsqueda de Mascotas ---
st.subheader("Buscar Mascota")
nombre_dueño = st.text_input("Nombre del Dueño") 
nombre_mascota = st.text_input("Nombre de la Mascota")

if st.button("Buscar Mascota"):
    cliente_encontrado = None
    
    # 1. Buscamos el cliente por nombre.
    # Utilizamos Utils.formatear_nombre para ser tolerantes a mayusculas y minusculas.
    for c in veterinaria.clientes:
        if Utils.formatear_nombre(c.nombre) == Utils.formatear_nombre(nombre_dueño):
            cliente_encontrado = c
            break

    mascota_encontrada = None
    
    if cliente_encontrado:
        # Buscar mascota por nombre dentro de ese cliente
        for m in cliente_encontrado.mascotas:
            if Utils.formatear_nombre(m.nombre) == Utils.formatear_nombre(nombre_mascota):
                mascota_encontrada = m
                break

    if mascota_encontrada:
        # Guardamos los objetos en la sesión
        st.session_state["cliente_actual_historial"] = cliente_encontrado 
        st.session_state["mascota_actual"] = mascota_encontrada
        st.success(f"✅ Mascota {mascota_encontrada.nombre}  encontrada. Aqui tiene su historial médico .")
    else:
        st.session_state["mascota_actual"] = None
        st.error("❌ Mascota o Dueño no encontrados.")

# Mostrar y Gestionar el historial 
if "mascota_actual" in st.session_state and st.session_state["mascota_actual"]:
    mascota = st.session_state["mascota_actual"]
    cliente = st.session_state["cliente_actual_historial"]

    st.write("---")
    st.subheader(f"Ficha médica de {mascota.nombre}")
    #Utilizamos tab para que se separe en dos formularios
    tab1, tab2 = st.tabs(["Historial Básico", "Añadir Datos"])

    with tab1: # Visualización del Historial
        st.write("#### Datos del Dueño y Paciente")
        st.write(f"**Dueño:** {cliente.nombre}") 
        st.write(f"**Raza:** {mascota.raza}")
        st.write(f"**Fecha Nacimiento:** {mascota.fecha_nacimiento.strftime('%d/%m/%Y')}") 

        st.write("#### Registros Técnicos")
        
        col_vacuna, col_peso = st.columns(2)
        with col_vacuna:
            st.write("##### Vacunas")
            #Aqui les traemos la informacion que se ha metido en añadir datos
            st.dataframe(pd.DataFrame({'Vacunas Registradas': mascota.historial_medico['vacunas']}), height=150)
        with col_peso:
            st.write("##### Peso (kg)")
            #Aqui les traemos la informacion que se ha metido en añadir datos
            st.dataframe(pd.DataFrame(mascota.historial_medico['peso']), height=150)
            
        st.write("#### Observaciones y Tratamientos")
        st.write(mascota.historial_medico['observaciones'])
        st.write(mascota.historial_medico['tratamientos'])


    with tab2: # Formularios para Añadir Datos
        st.subheader("Añadir Registros al Historial")
        
        # Formulario para añadir vacunas, llamamos a la funcion de veterinaria.py de añadir_vacunas
        with st.form("form_vacuna"):
            st.write(" **Nueva Vacuna**")
            nombre_vacuna = st.text_input("Nombre de la Vacuna", key="vac_nombre", value="")
            fecha_vacuna = st.date_input("Fecha de Aplicación", key="vac_fecha", value=date.today())
            vacuna_submit = st.form_submit_button("Registrar Vacuna")
            #Metemos la condicion de que el nombre de la vacuna no puede estar vacio
            if vacuna_submit:
                if nombre_vacuna:
                    veterinaria.anadir_vacuna(mascota, nombre_vacuna, fecha_vacuna)
                    st.success(f"Vacuna '{nombre_vacuna}' registrada.")
                else:
                    st.error("El nombre de la vacuna no puede estar vacío.")

        # Formulario para añadir peso, llamamos a la funcion de veterinaria.py de añadir_peso
        with st.form("form_peso"):
            st.write(" **Registro de Peso**")
            peso_kg = st.number_input("Peso (kg)", min_value=0.1, format="%.2f", key="peso_input")
            fecha_peso = st.date_input("Fecha de Medición", key="peso_fecha", value=date.today())
            peso_submit = st.form_submit_button("Registrar Peso")

            if peso_submit:
                veterinaria.anadir_peso(mascota, peso_kg, fecha_peso)
                st.success(f"Peso {peso_kg} kg registrado.")
                
        # Formulario para añadir observaciones y tratamientos,llamamos a anadir_observacion  anadir_tratamiento de veterinaria.py
        with st.form("form_obs_trat"):
            st.write(" **Observaciones / Tratamientos**")
            tipo_registro = st.radio("Tipo de Registro", ["Observación", "Tratamiento"], horizontal=True, key="reg_tipo")
            detalle = st.text_area("Detalles (Dosis, Diagnóstico, Notas)", height=80)
            fecha_registro = st.date_input("Fecha del Registro", key="obs_fecha", value=date.today())
            obs_submit = st.form_submit_button("Guardar Registro")
            
            if obs_submit:
                if detalle:
                    if tipo_registro == "Observación":
                        veterinaria.anadir_observacion(mascota, detalle, fecha_registro)
                        st.success("Observación guardada.")
                        st.rerun() # Aqui lo que hace el rerun es hacer que streamlit se actualice en cuanto le des a guardar registro 
                                   # y los datos que has añadido en añadir datos se vuelvan en historial medico.
                    else:
                        veterinaria.anadir_tratamiento(mascota, detalle, fecha_registro)
                        st.success("Tratamiento guardado.")
                        st.rerun() #
