import streamlit as st
import pandas as pd
from datetime import date
import sys
import os

# -------------------------------------------------------------------------
# CORRECCIÓN DEFINITIVA DE RUTAS
# -------------------------------------------------------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
# Ruta directa a la carpeta 'src'
path_to_src = os.path.abspath(os.path.join(current_dir, '..', '..', 'src'))

if path_to_src not in sys.path:
    sys.path.append(path_to_src)

try:
    # IMPORTACIÓN DIRECTA (Asegúrate de que el archivo es Veterinaria.py con mayúscula)
    from veterinaria import veterinaria
    from utils import utils
except ImportError as e:
    st.error(f"Error crítico: {e}")
    st.write("Ruta buscada:", path_to_src)
    st.stop()

# -------------------------------------------------------------------------
# LÓGICA DE LA PÁGINA
# -------------------------------------------------------------------------

st.set_page_config(page_title="Historial Médico", page_icon="🩺", layout="wide")

if "mi_clinica" not in st.session_state:
    st.session_state["mi_clinica"] = Veterinaria()

if "login_correcto" not in st.session_state or not st.session_state["login_correcto"]:
    st.warning("🔒 Debes iniciar sesión para acceder al historial.")
    st.stop()

st.title("🩺 Historial Médico y Tratamientos")
veterinaria = st.session_state["mi_clinica"]

# --- Búsqueda ---
st.subheader("🔍 Buscar Paciente")

with st.container(border=True): 
    col_dueño_input, col_mascota_input, col_btn = st.columns([2, 2, 1])
    
    with col_dueño_input:
        nombre_dueño = st.text_input("Nombre del Dueño", key="hist_dueño") 
    with col_mascota_input:
        nombre_mascota = st.text_input("Nombre de la Mascota", key="hist_mascota")
    with col_btn:
        st.write(" ") 
        if st.button("Buscar Mascota", type="primary"):
            cliente_encontrado = None
            
            nombre_dueño_formateado = Utils.formatear_nombre(nombre_dueño)
            for c in veterinaria.clientes:
                if Utils.formatear_nombre(c.nombre) == nombre_dueño_formateado:
                    cliente_encontrado = c
                    break

            mascota_encontrada = None
            if cliente_encontrado:
                nombre_mascota_formateado = Utils.formatear_nombre(nombre_mascota)
                for m in cliente_encontrado.mascotas:
                    if Utils.formatear_nombre(m.nombre) == nombre_mascota_formateado:
                        mascota_encontrada = m
                        break

            if mascota_encontrada:
                st.session_state["cliente_actual_historial"] = cliente_encontrado 
                st.session_state["mascota_actual"] = mascota_encontrada
                st.success(f"✅ Mascota **{mascota_encontrada.nombre}** encontrada.")
            else:
                st.session_state["mascota_actual"] = None
                st.error("❌ Mascota o Dueño no encontrados.")

# --- Gestión del Historial ---
if "mascota_actual" in st.session_state and st.session_state["mascota_actual"]:
    mascota = st.session_state["mascota_actual"]
    cliente = st.session_state["cliente_actual_historial"]

    st.write("---")
    st.subheader(f"Ficha Médica de {mascota.nombre}")
    
    tab1, tab2 = st.tabs(["📋 Historial Básico", "➕ Añadir Datos"])

    with tab1: 
        st.write("#### Datos del Paciente")
        c1, c2, c3 = st.columns(3)
        c1.metric("Dueño", cliente.nombre)
        c2.metric("Raza", mascota.raza)
        c3.metric("ID", mascota.id[:8])
        
        st.divider()
        c_vac, c_peso = st.columns(2)
        with c_vac:
            st.info("Vacunas")
            st.dataframe(pd.DataFrame({'Vacunas': mascota.historial_medico['vacunas']}), use_container_width=True)
        with c_peso:
            st.info("Peso")
            st.dataframe(pd.DataFrame(mascota.historial_medico['peso']), use_container_width=True)

    with tab2: 
        st.subheader("➕ Añadir Registros")
        with st.form("form_vacuna"):
            nom_vac = st.text_input("Nombre Vacuna")
            fecha_vac = st.date_input("Fecha", value=date.today())
            if st.form_submit_button("Guardar Vacuna"):
                if nom_vac:
                    mascota.historial_medico['vacunas'].append(f"{fecha_vac} - {nom_vac}")
                    st.success("Guardado")
                    st.rerun()