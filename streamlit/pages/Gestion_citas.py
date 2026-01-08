
import streamlit as st
import pandas as pd
from datetime import date
# Importamos nuestras funciones de base de datos
from db_utils import run_query, read_query, create_tables

st.set_page_config(page_title="Gestión de Citas", page_icon="📅", layout="wide")

def app():
    # Aseguramos que las tablas existan 
    create_tables()

    st.title("📅 Gestión de Citas")

    # Necesitamos la lista de mascotas para que el usuario elija, no escriba
    pacientes_db = read_query("SELECT id, nombre, propietario FROM pacientes")
    
    # Creamos un diccionario para el selectbox: "Toby (Dueño: Juan)" -> ID 1
    # Esto ayuda a diferenciar si hay dos perros llamados "Toby"
    opciones_pacientes = {}
    if pacientes_db:
        for p in pacientes_db:
            etiqueta = f"{p[1]} (Dueño: {p[2]})" # Ejemplo: Rex (Dueño: Ana)
            opciones_pacientes[etiqueta] = p[0] # Guardamos el ID asociado

    st.subheader("✍️ Programar Nueva Cita")

    with st.container(border=True): 
        with st.form("form_cita"):
            
            col_mascota, col_vet = st.columns(2)
            
            with col_mascota:
                if not opciones_pacientes:
                    st.warning(" No hay pacientes registrados. Ve a 'Registrar Cliente' primero.")
                    paciente_seleccionado_nombre = None
                else:
                    paciente_seleccionado_nombre = st.selectbox(
                        "Seleccionar Paciente", 
                        options=list(opciones_pacientes.keys())
                    )

            with col_vet:
                veterinario_responsable = st.selectbox(
                    "Veterinario Responsable", 
                    ["Dr. Rufino", "Dra. Ana", "Dr. Tomás"]
                )
            
            st.divider()
            
            col_fecha, col_hora = st.columns(2)
            
            with col_fecha:
                fecha_cita = st.date_input("Fecha", value=date.today())
            with col_hora:
                # Generamos horas de 09:00 a 20:00
                opciones_hora = [f"{h:02d}:00" for h in range(9, 21)] 
                hora_cita = st.selectbox("Hora", options=opciones_hora)
                
            motivo = st.text_area("Motivo de la consulta", height=80)
            
            submitted = st.form_submit_button("✅ Programar Cita", type="primary")
            
            if submitted:
                if paciente_seleccionado_nombre:
                    # Recuperamos el ID real usando el nombre seleccionado
                    paciente_id = opciones_pacientes[paciente_seleccionado_nombre]
                    
                    # Guardamos en SQLite
                    query = """
                        INSERT INTO citas (paciente_id, fecha, hora, motivo, veterinario) 
                        VALUES (?, ?, ?, ?, ?)
                    """
                    params = (paciente_id, str(fecha_cita), str(hora_cita), motivo, veterinario_responsable)
                    
                    run_query(query, params)
                    st.success(f"✅ Cita programada para **{paciente_seleccionado_nombre}** el {fecha_cita} a las {hora_cita}.")
                else:
                    st.error("❌ No has seleccionado ningún paciente válido.")

    # --- VISUALIZACIÓN DE CITAS ---
    st.write("---")
    st.subheader("📋 Próximas Citas")

    # Hacemos un JOIN para traer el nombre del paciente en vez de solo su ID número
    query_view = """
        SELECT 
            citas.fecha, 
            citas.hora, 
            pacientes.nombre, 
            pacientes.propietario, 
            citas.veterinario, 
            citas.motivo 
        FROM citas
        JOIN pacientes ON citas.paciente_id = pacientes.id
        ORDER BY citas.fecha DESC, citas.hora ASC
    """
    datos_citas = read_query(query_view)

    if datos_citas:
        df = pd.DataFrame(datos_citas, columns=["Fecha", "Hora", "Mascota", "Dueño", "Veterinario", "Motivo"])
        st.dataframe(df, use_container_width=True, height=400)
    else:
        st.info(" No hay citas programadas actualmente en la base de datos.")

# Esto permite que funcione si ejecutas la página directamente o si la importas
if __name__ == "__main__":
    app()