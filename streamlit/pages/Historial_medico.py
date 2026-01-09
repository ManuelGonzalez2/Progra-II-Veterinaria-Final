import streamlit as st
import pandas as pd
from datetime import date
# Importamos las funciones de tu base de datos
from db_utils import run_query, read_query

# 1. CONFIGURACIÓN DE PÁGINA (Siempre lo primero)
st.set_page_config(page_title="Historial Médico", page_icon="🩺", layout="wide")


# Verificar si el usuario ha iniciado sesión
if "login_correcto" not in st.session_state or not st.session_state["login_correcto"]:
    st.warning("⚠️ Por favor, inicia sesión en la página de Inicio (Home) para acceder a este módulo.")
    st.info("Haz clic en 'Home' en el menú lateral.")
    st.stop() # Esto detiene la ejecución del resto de la página

def app():
    st.title("🩺 Historial Médico y Tratamientos")

    # 2. CARGA DE DATOS DE PACIENTES
    # Ordenamos por nombre para que la lista sea estable
    pacientes_db = read_query("SELECT id, nombre, propietario, raza FROM pacientes ORDER BY nombre ASC")
    
    # Si no hay pacientes, mostramos aviso pero NO paramos el script (para evitar pantalla en blanco)
    if not pacientes_db:
        st.warning("⚠️ No se encontraron pacientes en la base de datos. Por favor, registra uno primero.")
        return

    # Creamos el diccionario para el selector: "Nombre (Dueño) - Raza" -> ID
    dict_pacientes = {f"{p[1]} (Dueño: {p[2]}) - {p[3]}": p[0] for p in pacientes_db}
    lista_nombres = list(dict_pacientes.keys())

    # 3. SELECTOR DE PACIENTE
    st.subheader("🔍 Seleccionar Paciente")
    
    # Usamos una 'key' para que Streamlit mantenga la selección incluso al recargar
    seleccion_nombre = st.selectbox(
        "Busca y selecciona un paciente:", 
        options=lista_nombres,
        key="selector_historial_medico"
    )
    
    # Obtenemos el ID del paciente seleccionado
    id_paciente = dict_pacientes[seleccion_nombre]
    
    # Recuperamos la info detallada del paciente actual
    info_paciente = read_query("SELECT nombre, raza, propietario FROM pacientes WHERE id = ?", (id_paciente,))
    
    if info_paciente:
        nombre_p, raza_p, dueno_p = info_paciente[0]
        
        # Panel visual de información
        st.divider()
        col1, col2, col3 = st.columns(3)
        col1.metric("🐶 Paciente", nombre_p)
        col2.metric("👤 Propietario", dueno_p)
        col3.metric("🧬 Raza", raza_p)
        st.divider()

        # 4. PESTAÑAS (TABS)
        tab_ver, tab_anadir = st.tabs(["📋 Ver Historial Completo", "➕ Añadir Nueva Visita/Vacuna"])

        # --- TAB: VER HISTORIAL ---
        with tab_ver:
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
                st.info(f"El historial de **{nombre_p}** todavía está vacío.")

        # --- TAB: AÑADIR ENTRADA ---
        with tab_anadir:
            st.info(f"Vas a añadir una nueva entrada al historial de: **{nombre_p}**")
            
            # Formulario para evitar recargas accidentales
            with st.form("nuevo_registro_historial", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    fecha_v = st.date_input("Fecha", value=date.today())
                with c2:
                    tipo_v = st.selectbox("Tipo de Visita", ["Consulta", "Vacunación", "Cirugía", "Urgencia", "Control"])
                
                desc_v = st.text_area("Descripción / Diagnóstico")
                trata_v = st.text_input("Tratamiento / Medicación / Vacuna")
                
                # Botón de envío
                boton_guardar = st.form_submit_button("💾 Guardar en el Historial", type="primary")

                if boton_guardar:
                    if not desc_v.strip():
                        st.error("❌ Por favor, indica una descripción o diagnóstico.")
                    else:
                        # Preparamos el texto final
                        descripcion_final = f"[{tipo_v.upper()}] {desc_v}"
                        
                        # Guardamos en la BD usando el id_paciente que seleccionamos arriba
                        query_insert = "INSERT INTO historial (paciente_id, fecha, descripcion, tratamiento) VALUES (?, ?, ?, ?)"
                        run_query(query_insert, (id_paciente, str(fecha_v), descripcion_final, trata_v))
                        
                        st.success(f"✅ ¡Historial actualizado para {nombre_p}!")
                        st.rerun()

# 5. EJECUCIÓN (Esto es lo que hace que la página no salga en blanco)
if __name__ == "__main__":
    app()