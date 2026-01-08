import streamlit as st


st.set_page_config(page_title="Curae Veterinaria", page_icon="🏥")

st.title("Curae Veterinaria - Inicio de Sesión")



if "login_correcto" not in st.session_state:
    st.session_state["login_correcto"] = False

#LÓGICA DE LOGIN 

if st.session_state["login_correcto"]:
    
    st.success(" ¡Bienvenido al Sistema de Gestión Veterinaria!")
    
    st.write("### 👈 Utiliza el menú lateral para navegar.")
    
    st.info("""
    **Módulos disponibles:**
    * 📅 **Citas:** Calendario y programación.
    * 🩺 **Historial:** Fichas médicas y tratamientos.
    * 👤 **Registrar:** Crea nuevos clientes y sus mascotas.
    * 📋 **Clientes:** Gestión de dueños.
    * 🐾 **Pacientes:** Ver listado y buscar mascotas.
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