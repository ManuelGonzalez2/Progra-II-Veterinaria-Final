import sys
import os
# La siguiente linea de codigo es un ajuste de ruta para que pueda encontrar la carpeta src
# Es la solución de emergencia para que los ficheros de pages reconozcan al motor.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import streamlit as st
from src import Veterinaria, Utils
from datetime import date
import pandas as pd

# --- Configuración de la Página de Streamlit ---
st.set_page_config(page_title="Historial Médico", page_icon="🩺", layout="wide")

# Inicialización de la clase Veterinaria (Singleton)
if "mi_clinica" not in st.session_state:
    st.session_state["mi_clinica"] = Veterinaria()

# Seguridad: Si no está logueado, detener la ejecución
if "login_correcto" not in st.session_state or not st.session_state["login_correcto"]:
    st.warning("🔒 Debes iniciar sesión para acceder al historial.")
    st.stop()

st.title("🩺 Historial Médico y Tratamientos")
veterinaria = st.session_state["mi_clinica"]

# --- 1. Búsqueda de Mascotas (Mejoras estéticas) ---
st.subheader("🔍 Buscar Paciente")

# Usamos un contenedor para la búsqueda
with st.container(border=True): 
    col_dueño_input, col_mascota_input, col_btn = st.columns([2, 2, 1])
    
    with col_dueño_input:
        nombre_dueño = st.text_input("Nombre del Dueño", key="hist_dueño") 
    with col_mascota_input:
        nombre_mascota = st.text_input("Nombre de la Mascota", key="hist_mascota")
    with col_btn:
        st.write(" ") # Espacio para alinear el botón
        if st.button("Buscar Mascota", type="primary"):
            cliente_encontrado = None
            
            # 1. Buscamos el cliente por nombre
            nombre_dueño_formateado = Utils.formatear_nombre(nombre_dueño)
            for c in veterinaria.clientes:
                if Utils.formatear_nombre(c.nombre) == nombre_dueño_formateado:
                    cliente_encontrado = c
                    break

            mascota_encontrada = None
            
            if cliente_encontrado:
                # 2. Buscar mascota por nombre dentro de ese cliente
                nombre_mascota_formateado = Utils.formatear_nombre(nombre_mascota)
                for m in cliente_encontrado.mascotas:
                    if Utils.formatear_nombre(m.nombre) == nombre_mascota_formateado:
                        mascota_encontrada = m
                        break

            if mascota_encontrada:
                st.session_state["cliente_actual_historial"] = cliente_encontrado 
                st.session_state["mascota_actual"] = mascota_encontrada
                st.success(f"✅ Mascota **{mascota_encontrada.nombre}** encontrada. ID: {mascota_encontrada.id[:8]}...")
                st.balloons() # Pequeño efecto visual de éxito
            else:
                st.session_state["mascota_actual"] = None
                st.error("❌ Mascota o Dueño no encontrados.")

# Mostrar y Gestionar el historial 
if "mascota_actual" in st.session_state and st.session_state["mascota_actual"]:
    mascota = st.session_state["mascota_actual"]
    cliente = st.session_state["cliente_actual_historial"]

    st.write("---")
    st.subheader(f"Ficha Médica de {mascota.nombre} ({mascota.especie.title()})")
    
    tab1, tab2 = st.tabs(["📋 Historial Básico", "➕ Añadir Datos"])

    with tab1: # Visualización del Historial
        st.write("#### Datos del Dueño y Paciente")
        
        # Uso de st.metric para la "gracia" visual
        col_dueño, col_raza, col_nac, col_id = st.columns(4)
        
        col_dueño.metric(label="Dueño", value=cliente.nombre)
        col_raza.metric(label="Raza", value=mascota.raza.title())
        col_nac.metric(label="Fecha Nacimiento", value=mascota.fecha_nacimiento.strftime('%d/%m/%Y'))
        col_id.metric(label="ID Mascota", value=mascota.id[:8] + "...")
        
        st.divider()

        st.write("#### Registros Técnicos")
        
        col_vacuna, col_peso = st.columns(2)
        with col_vacuna:
            st.info("##### 💉 Vacunas")
            # Ajustamos la altura y el ancho del dataframe
            df_vacunas = pd.DataFrame({'Vacunas Registradas': mascota.historial_medico['vacunas']})
            st.dataframe(df_vacunas, use_container_width=True, hide_index=True)
        with col_peso:
            st.info("##### ⚖️ Peso (kg)")
            # Ajustamos el dataframe de peso
            df_peso = pd.DataFrame(mascota.historial_medico['peso'])
            st.dataframe(df_peso, use_container_width=True, hide_index=True)
            
        st.write("#### Notas y Tratamientos")
        
        col_obs, col_trat = st.columns(2)
        with col_obs:
            st.warning("##### 📝 Observaciones")
            for obs in mascota.historial_medico['observaciones']:
                 st.write(obs)
        with col_trat:
            st.error("##### 💊 Tratamientos")
            for trat in mascota.historial_medico['tratamientos']:
                 st.write(trat)


    with tab2: # Formularios para Añadir Datos
        st.subheader("➕ Añadir Registros al Historial")
        
        col_vac, col_peso = st.columns(2)
        
        with col_vac:
            # Formulario para añadir vacunas
            with st.form("form_vacuna", border=True):
                st.write(" **💉 Registrar Nueva Vacuna**")
                nombre_vacuna = st.text_input("Nombre de la Vacuna", key="vac_nombre", value="")
                fecha_vacuna = st.date_input("Fecha de Aplicación", key="vac_fecha", value=date.today())
                vacuna_submit = st.form_submit_button("Guardar Vacuna", type="primary")