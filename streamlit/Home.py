import streamlit as st

# Configuración básica de la página
st.set_page_config(page_title="Curae Veterinaria", page_icon="🏥")

st.title("Curae Veterinaria - Inicio de Sesión")

# --- GESTIÓN DE ESTADO (SESSION STATE) ---
# Ya NO necesitamos inicializar la clase Veterinaria aquí.
# La base de datos se encarga de guardar los datos sola.
# Solo necesitamos saber si el usuario se ha logueado o no.

if "login_correcto" not in st.session_state:
    st.session_state["login_correcto"] = False

# --- LÓGICA DE LOGIN ---

if st.session_state["login_correcto"]:
    # Si ya está logueado, le damos la bienvenida
    st.success("✅ ¡Bienvenido al Sistema de Gestión Veterinaria!")
    
    st.write("### 👈 Utiliza el menú lateral para navegar.")
    
    st.info("""
    **Módulos disponibles:**
    * 👤 **Registrar:** Crea nuevos clientes y sus mascotas.
    * 🐾 **Pacientes:** Ver listado y buscar mascotas.
    * 📋 **Clientes:** Gestión de dueños.
    * 📅 **Citas:** Calendario y programación.
    * 🩺 **Historial:** Fichas médicas y tratamientos.
    """)
    
    st.divider()
    
    if st.button("🔒 Cerrar Sesión"):
        st.session_state["login_correcto"] = False
        st.rerun()

else:
    # Si NO está logueado, mostramos el formulario
    st.markdown("#### Por favor, introduzca sus credenciales para acceder.")
    
    with st.form("login_form"):
        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Iniciar Sesión")

        if submit:
            # Las credenciales son : ADMIN y 1234
            if usuario == "ADMIN" and password == "1234":
                st.session_state["login_correcto"] = True
                st.balloons()
                st.rerun() # Recarga para quitar el formulario y mostrar el menú
            else:
                st.error("❌ El usuario o la contraseña son incorrectos")