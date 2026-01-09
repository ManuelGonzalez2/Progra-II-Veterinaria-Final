import streamlit as st
import pandas as pd
# Importamos nuestras herramientas de base de datos
from db_utils import read_query, run_query

st.set_page_config(page_title="Ver Clientes", page_icon="📋", layout="wide")

# Verificar si el usuario ha iniciado sesión
if "login_correcto" not in st.session_state or not st.session_state["login_correcto"]:
    st.warning("⚠️ Por favor, inicia sesión en la página de Inicio (Home) para acceder a este módulo.")
    st.info("Haz clic en 'Home' en el menú lateral.")
    st.stop() # Esto detiene la ejecución del resto de la página

def app():
    st.title("🧑‍💻 Clientes Registrados")
    st.caption("Listado de dueños únicos (agrupados por email).")

    #Permite que la aplicación te confirme que algo ha salido bien (o mal) justo después de que la 
    #página se haya reiniciado. Lo lees una vez y se autodestruye para no molestar.
    if "mensaje_status" in st.session_state:
        if st.session_state["mensaje_status"]["tipo"] == "success":
            st.success(st.session_state["mensaje_status"]["texto"])
        else:
            st.error(st.session_state["mensaje_status"]["texto"])
        # Borramos el mensaje para que no salga eternamente
        del st.session_state["mensaje_status"]


    st.subheader("BBDD de Dueños Activos")

    # Primero agrupamos por email (GROUP BY email) para que cada dueño salga solo una vez.
    # Despues contamos cuántas filas tiene ese email (COUNT(id)) para saber cuántas mascotas tiene.
    query = """
        SELECT 
            propietario, 
            telefono, 
            email, 
            COUNT(id) as total_mascotas 
        FROM pacientes 
        GROUP BY email
    """
    datos = read_query(query)

    if not datos:
        st.info(" Aún no hay clientes registrados en la base de datos.")
    else:
        # Creamos el DataFrame
        df = pd.DataFrame(datos, columns=["Nombre Dueño", "Teléfono", "Email", "Mascotas Registradas"])
        
        st.dataframe(
            df, 
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    # Dar de Baja un Cliente 
    st.subheader("❌ Dar de Baja un Cliente")
    st.warning("⚠️ CUIDADO: Esta acción borrará al cliente, a TODAS sus mascotas y sus citas asociadas.")

    with st.form("form_eliminar", border=True):
        col_input, col_button = st.columns([3, 1])
        
        with col_input:
            # Usamos un selectbox en vez de texto libre para evitar errores de dedo al borrar
            lista_emails = [row[2] for row in datos] if datos else []
            email_eliminar = st.selectbox("Seleccionar Cliente a Eliminar", lista_emails) if lista_emails else st.text_input("Email")
        
        with col_button:
            st.write(" ") 
            confirm_button = st.form_submit_button("🗑️ Eliminar Definitivamente", type="primary")
        
        if confirm_button:
            if email_eliminar:

                try:
                    # 1. Primero averiguamos los IDs de las mascotas de este dueño
                    mascotas = read_query("SELECT id FROM pacientes WHERE email = ?", (email_eliminar,))
                    ids_mascotas = [m[0] for m in mascotas]
                    
                    if ids_mascotas:
                        # Convertimos la lista de IDs a formato string para SQL (ej: "1, 2, 5")
                        ids_str = ', '.join(map(str, ids_mascotas))

                        # 2. Borramos Citas asociadas a esas mascotas

                        for mid in ids_mascotas:
                            run_query("DELETE FROM citas WHERE paciente_id = ?", (mid,))
                            run_query("DELETE FROM historial WHERE paciente_id = ?", (mid,))
                    
                    # 3. Finalmente borramos al dueño/mascotas de la tabla principal
                    run_query("DELETE FROM pacientes WHERE email = ?", (email_eliminar,))
                    
                    # Guardamos mensaje y recargamos
                    st.session_state["mensaje_status"] = {
                        "tipo": "success", 
                        "texto": f"✅ Cliente {email_eliminar} y sus datos han sido eliminados."
                    }
                    st.rerun()
                    
                except Exception as e:
                    st.session_state["mensaje_status"] = {
                        "tipo": "error", 
                        "texto": f"❌ Error al eliminar: {e}"
                    }
                    st.rerun()
            else:
                st.error("No hay clientes seleccionables.")

if __name__ == "__main__":
    app()