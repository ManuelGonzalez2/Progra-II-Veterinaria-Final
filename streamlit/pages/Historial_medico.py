import streamlit as st
import pandas as pd
from datetime import date
# Importamos las funciones de nuestra base de datos
from db_utils import run_query, read_query

st.set_page_config(page_title="Historial Médico", page_icon="🩺", layout="wide")

def app():
    st.title("🩺 Historial Médico y Tratamientos")

    # --- 1. SELECCIÓN DE PACIENTE (Buscador Inteligente) ---
    # Traemos todos los pacientes para el buscador
    # Recuperamos ID, Nombre, Propietario y Raza
    pacientes_db = read_query("SELECT id, nombre, propietario, raza FROM pacientes")
    
    if not pacientes_db:
        st.warning("⚠️ No hay pacientes registrados. Ve a 'Registrar Cliente' para empezar.")
        st.stop()

    # Creamos el diccionario para el desplegable
    # Clave: "Rex (Dueño: Ana) - Pastor Alemán" -> Valor: ID del paciente
    dict_pacientes = {f"{p[1]} (Dueño: {p[2]}) - {p[3]}": p[0] for p in pacientes_db}

    # Selector en la barra principal o arriba
    st.subheader("🔍 Seleccionar Paciente")
    nombre_seleccionado = st.selectbox("Buscar por nombre:", list(dict_pacientes.keys()))
    
    # Obtenemos el ID real del paciente seleccionado
    id_paciente = dict_pacientes[nombre_seleccionado]
    
    # Recuperamos datos "bonitos" para mostrar (Nombre, Raza, Dueño)
    # Volvemos a buscar info específica de este ID para asegurarnos
    info_paciente = read_query("SELECT nombre, raza, propietario FROM pacientes WHERE id = ?", (id_paciente,))
    nombre_p, raza_p, dueno_p = info_paciente[0]

    # --- 2. MOSTRAR DATOS BÁSICOS ---
    st.divider()
    col1, col2, col3 = st.columns(3)
    col1.metric("🐶 Paciente", nombre_p)
    col2.metric("👤 Propietario", dueno_p)
    col3.metric("rga Raza", raza_p)
    st.divider()

    # --- 3. PESTAÑAS DE GESTIÓN ---
    tab_ver, tab_anadir = st.tabs(["📋 Ver Historial Completo", "➕ Añadir Nueva Visita/Vacuna"])

    # --- TAB 1: VER HISTORIAL ---
    with tab_ver:
        # Leemos todo el historial de ESTE paciente ordenado por fecha (el más reciente arriba)
        query_historial = """
            SELECT fecha, descripcion, tratamiento 
            FROM historial 
            WHERE paciente_id = ? 
            ORDER BY fecha DESC
        """
        datos_historial = read_query(query_historial, (id_paciente,))

        if datos_historial:
            df = pd.DataFrame(datos_historial, columns=["Fecha", "Detalles / Diagnóstico", "Tratamiento / Notas"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info(f"El historial de {nombre_p} está vacío.")

    # --- TAB 2: AÑADIR NUEVA ENTRADA ---
    with tab_anadir:
        st.write(f"Agregando entrada al historial de **{nombre_p}**")
        
        with st.form("form_historial"):
            col_fecha, col_tipo = st.columns(2)
            
            with col_fecha:
                fecha = st.date_input("Fecha de visita", value=date.today())
            
            with col_tipo:
                tipo_evento = st.selectbox("Tipo de Evento", ["Consulta General", "Vacunación", "Control de Peso", "Cirugía", "Urgencia"])

            # Inputs de texto
            descripcion_input = st.text_area("Diagnóstico / Descripción")
            tratamiento_input = st.text_input("Tratamiento recetado / Vacuna aplicada")

            submitted = st.form_submit_button("💾 Guardar en Historial", type="primary")

            if submitted:
                # Concatenamos el TIPO con la descripción para que se vea claro en la tabla
                # Ej: "[VACUNACIÓN] Rabia anual"
                descripcion_final = f"[{tipo_evento.upper()}] {descripcion_input}"
                
                query_insert = """
                    INSERT INTO historial (paciente_id, fecha, descripcion, tratamiento) 
                    VALUES (?, ?, ?, ?)
                """
                run_query(query_insert, (id_paciente, str(fecha), descripcion_final, tratamiento_input))
                
                st.success("✅ Entrada guardada correctamente.")
                st.rerun() # Recargamos para que salga en la pestaña de "Ver Historial" al momento

if __name__ == "__main__":
    app()