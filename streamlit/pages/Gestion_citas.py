import sys
import os
# Ajuste de ruta para reconocer la carpeta src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import streamlit as st
import pandas as pd
from datetime import date
# Importamos Utils para usar la función de formatear nombre y buscar mejor
from src import Veterinaria, Utils 

# --- Configuración de la Página de Streamlit ---
# Usamos un layout más amplio para la tabla de citas
st.set_page_config(page_title="Gestión de Citas", page_icon="📅", layout="wide")

# Inicialización de la clase Veterinaria (Singleton)
if "mi_clinica" not in st.session_state:
    st.session_state["mi_clinica"] = Veterinaria()

# Control de acceso
if "login_correcto" not in st.session_state or not st.session_state["login_correcto"]:
    st.warning("🔒 Debes iniciar sesión para acceder a la gestión de citas.")
    st.stop()

st.title("📅 Gestión de Citas")
veterinaria = st.session_state["mi_clinica"]

# --- 1. Formulario para Crear Cita (Mejoras estéticas con st.columns) ---
st.subheader("✍️ Programar Nueva Cita")

# Usamos un contenedor 'info' para que el formulario tenga un ligero color de fondo
with st.container(border=True): 
    with st.form("form_cita"):
        st.caption("Detalles del Dueño y el Paciente")
        
        # Columnas para mejor distribución de los inputs
        col_dueño, col_mascota = st.columns(2)
        with col_dueño:
            nombre_dueño = st.text_input("Nombre Completo del Dueño", key="nombre_dueño_cita") 
        with col_mascota:
            nombre_mascota = st.text_input("Nombre de la Mascota", key="mascota_cita")
        
        st.divider()
        st.caption("Detalles de la Cita")
        col1, col2, col3 = st.columns([1.5, 1, 2]) # 3 Columnas
        
        with col1:
            fecha_cita = st.date_input("Fecha", value=date.today())
        with col2:
            # Lista de horas comunes para facilitar la entrada de datos
            opciones_hora = [f"{h:02d}:00" for h in range(9, 20)] 
            hora_cita = st.selectbox("Hora", options=opciones_hora)
            
        with col3:
            veterinario_responsable = st.selectbox("Veterinario Responsable", ["Dr. Rufino", "Dra. Ana", "Dr. Tomás"])
            
        motivo = st.text_area("Motivo de la Cita (Ej: Chequeo anual, Vacuna, Emergencia)", height=80)
        
        # Botón con color primario para destacar la acción
        submitted = st.form_submit_button("✅ Programar Cita", type="primary")
        
        # --- Lógica de Búsqueda y Creación ---
        if submitted:
            cliente_encontrado = None
            
            # 1. Buscamos el cliente por nombre
            nombre_dueño_formateado = Utils.formatear_nombre(nombre_dueño)
            for c in veterinaria.clientes:
                if Utils.formatear_nombre(c.nombre) == nombre_dueño_formateado:
                    cliente_encontrado = c
                    break

            if not cliente_encontrado:
                st.error("❌ Error: Cliente no encontrado por ese nombre. Asegúrate de que esté registrado.")
            else:
                # 2. Buscamos la mascota asociada a ese cliente.
                nombre_mascota_formateado = Utils.formatear_nombre(nombre_mascota)
                mascota_encontrada = next(
                    (m for m in cliente_encontrado.mascotas if Utils.formatear_nombre(m.nombre) == nombre_mascota_formateado), None 
                )
                
                if mascota_encontrada:
                    # 3. Creamos y registramos la cita (llama a la función que usa SQLite)
                    if veterinaria.crear_cita(fecha_cita, hora_cita, motivo, veterinario_responsable, mascota_encontrada):
                        st.success(f"✅ Cita programada para **{mascota_encontrada.nombre}** (Dueño: {cliente_encontrado.nombre}) con {veterinario_responsable}.")
                    else:
                        st.error("❌ Error al guardar la cita en la base de datos.")

                else:
                    st.error(f"❌ Error: Mascota **'{nombre_mascota}'** no registrada para el cliente {cliente_encontrado.nombre}.")


# --- 2. Visualización de Citas Programadas ---
st.write("---")
st.subheader("📋 Citas Programadas")

if veterinaria.citas:
    # 1. Preparamos los datos
    datos = {
        "Fecha": [c.fecha.strftime('%d/%m/%Y') for c in veterinaria.citas],
        "Hora": [c.hora for c in veterinaria.citas],
        "Mascota": [c.mascota.nombre for c in veterinaria.citas],
        # Asumimos que c.mascota.cliente.nombre es accesible desde la lógica de carga de Veterinaria
        "Dueño": [c.mascota.cliente.nombre for c in veterinaria.citas], 
        "Veterinario": [c.veterinario for c in veterinaria.citas],
        "Motivo": [c.motivo for c in veterinaria.citas]
    }
    df = pd.DataFrame(datos)
    
    # 2. Mostramos la tabla con un encabezado de texto más grande
    st.dataframe(
        df, 
        use_container_width=True, 
        height=400, # Altura fija para la tabla
        column_order=("Fecha", "Hora", "Mascota", "Dueño", "Veterinario", "Motivo") # Orden de las columnas
    )
else:
    st.info("ℹ️ No hay citas programadas actualmente.")