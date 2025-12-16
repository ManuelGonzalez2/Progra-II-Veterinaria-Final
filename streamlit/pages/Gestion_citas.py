import streamlit as st
import pandas as pd
from datetime import date
import sys
import os

# -------------------------------------------------------------------------
# CORRECCIÓN DEFINITIVA DE RUTAS
# -------------------------------------------------------------------------
# 1. Localizamos dónde está este archivo
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Construimos la ruta DIRECTA a la carpeta 'src'
# Subimos dos niveles (..) y entramos a 'src'
path_to_src = os.path.abspath(os.path.join(current_dir, '..', '..', 'src'))

# 3. Añadimos esa ruta específica al sistema
if path_to_src not in sys.path:
    sys.path.append(path_to_src)

# 4. Importamos DIRECTAMENTE (sin poner 'src.')
# Si tus archivos se llaman 'veterinaria.py' en minúscula, cambia esto a 'from veterinaria import Veterinaria'
try:
    from veterinaria import veterinaria
    from utils import utils
except ImportError as e:
    st.error(f"Error crítico: {e}")
    st.write("Ruta que Python está intentando leer:", path_to_src)
    st.stop()

# -------------------------------------------------------------------------
# LÓGICA DE LA PÁGINA (Igual que antes)
# -------------------------------------------------------------------------

st.set_page_config(page_title="Gestión de Citas", page_icon="📅", layout="wide")

if "mi_clinica" not in st.session_state:
    st.session_state["mi_clinica"] = Veterinaria()

if "login_correcto" not in st.session_state or not st.session_state["login_correcto"]:
    st.warning("🔒 Debes iniciar sesión para acceder a la gestión de citas.")
    st.stop()

st.title("📅 Gestión de Citas")
veterinaria = st.session_state["mi_clinica"]

# --- Formulario para Crear Cita ---
st.subheader("✍️ Programar Nueva Cita")

with st.container(border=True): 
    with st.form("form_cita"):
        st.caption("Detalles del Dueño y el Paciente")
        
        col_dueño, col_mascota = st.columns(2)
        with col_dueño:
            nombre_dueño = st.text_input("Nombre Completo del Dueño", key="nombre_dueño_cita") 
        with col_mascota:
            nombre_mascota = st.text_input("Nombre de la Mascota", key="mascota_cita")
        
        st.divider()
        col1, col2, col3 = st.columns([1.5, 1, 2]) 
        
        with col1:
            fecha_cita = st.date_input("Fecha", value=date.today())
        with col2:
            opciones_hora = [f"{h:02d}:00" for h in range(9, 20)] 
            hora_cita = st.selectbox("Hora", options=opciones_hora)
        with col3:
            veterinario_responsable = st.selectbox("Veterinario Responsable", ["Dr. Rufino", "Dra. Ana", "Dr. Tomás"])
            
        motivo = st.text_area("Motivo", height=80)
        submitted = st.form_submit_button("✅ Programar Cita", type="primary")
        
        if submitted:
            cliente_encontrado = None
            nombre_dueño_formateado = Utils.formatear_nombre(nombre_dueño)
            
            # Buscar Cliente
            for c in veterinaria.clientes:
                if Utils.formatear_nombre(c.nombre) == nombre_dueño_formateado:
                    cliente_encontrado = c
                    break

            if not cliente_encontrado:
                st.error("❌ Error: Cliente no encontrado.")
            else:
                # Buscar Mascota
                nombre_mascota_formateado = Utils.formatear_nombre(nombre_mascota)
                mascota_encontrada = next(
                    (m for m in cliente_encontrado.mascotas if Utils.formatear_nombre(m.nombre) == nombre_mascota_formateado), None 
                )
                
                if mascota_encontrada:
                    if veterinaria.crear_cita(fecha_cita, hora_cita, motivo, veterinario_responsable, mascota_encontrada):
                        st.success(f"✅ Cita programada para **{mascota_encontrada.nombre}**.")
                    else:
                        st.error("❌ Error al guardar.")
                else:
                    st.error(f"❌ Mascota no encontrada para este cliente.")

# --- Visualización ---
st.write("---")
st.subheader("📋 Citas Programadas")

if veterinaria.citas:
    datos = {
        "Fecha": [c.fecha.strftime('%d/%m/%Y') for c in veterinaria.citas],
        "Hora": [c.hora for c in veterinaria.citas],
        "Mascota": [c.mascota.nombre for c in veterinaria.citas],
        "Dueño": [c.mascota.cliente.nombre for c in veterinaria.citas], 
        "Veterinario": [c.veterinario for c in veterinaria.citas],
        "Motivo": [c.motivo for c in veterinaria.citas]
    }
    st.dataframe(pd.DataFrame(datos), use_container_width=True, height=400)
else:
    st.info("ℹ️ No hay citas programadas actualmente.")