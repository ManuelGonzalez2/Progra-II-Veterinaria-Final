import sys
import os
# La siguiente linea de codigo es un ajuste de ruta para que pueda encontrar la carpeta src
# Es la solución de emergencia para que los ficheros de pages reconozcan al motor.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import streamlit as st
from src.veterinaria import Veterinaria
from src.utils import Utils
from datetime import date

# --- Configuración de la Página de Streamlit ---
st.set_page_config(page_title="Registrar Cliente y Mascota", page_icon="👤")

# Inicialización de la clase Veterinaria (Singleton)
if "mi_clinica" not in st.session_state:
    st.session_state["mi_clinica"] = Veterinaria()


# Seguridad: Si no está logueado, detener la ejecución
if "login_correcto" not in st.session_state or not st.session_state["login_correcto"]:
    st.warning("🔒 Debes iniciar sesión para acceder al registro.")
    st.stop()

st.title("👤 Registrar Cliente y Mascota")
st.caption("Complete todos los campos para registrar un nuevo dueño y su paciente.")

veterinaria = st.session_state["mi_clinica"]

# Usamos un contenedor principal con borde para el formulario
with st.form("registro_completo", border=True):
    st.subheader("Datos de Registro")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("#### 1. Datos del Dueño (Cliente)")
        nombre = st.text_input("Nombre Completo", max_chars=50, key="c_nombre")
        telefono = st.text_input("Teléfono", max_chars=15, key="c_telf")
        email = st.text_input("Email", key="c_email")
    
    with col2:
        st.write("#### 2. Datos de la Mascota")
        nombre_mascota = st.text_input("Nombre de la Mascota", key="m_nombre")
        # Opciones predefinidas y formateo de texto
        especie = st.selectbox("Especie", ["Perro", "Gato", "Ave", "Conejo", "Otro"], key="m_especie")
        raza = st.text_input("Raza", key="m_raza")
        fecha_nac = st.date_input("Fecha de Nacimiento", value=date.today(), key="m_fnac")
    
    st.write("---")
    # Botón de envío con color primario
    submitted = st.form_submit_button("✅ Registrar Cliente y Mascota", type="primary")

    if submitted:
        # --- Validaciones ---
        if not nombre or not email or not nombre_mascota:
             st.error("❌ Faltan campos obligatorios (Nombre, Email o Nombre Mascota).")
        elif not Utils.validar_email(email):
            st.error("❌ El email no es válido. Debe contener @ y un punto.")
        else:
            # 1. Registrar Cliente (la función usa el email para evitar duplicados en DB)
            nombre_formateado = Utils.formatear_nombre(nombre)
            cliente_creado = veterinaria.registrar_cliente(
                nombre_formateado, 
                telefono, 
                email
            )
            
            if cliente_creado:
                # 2. Registrar Mascota (asociada al ID del cliente creado)
                # NOTA: Tu función registrar_mascota en veterinaria.py espera el email,
                # pero en un sistema con IDs es mejor usar el ID del objeto creado.
                # Como tu funcion fue definida para usar email, la mantendremos así, 
                # pero la recomendación es cambiarla en veterinaria.py para que use cliente_creado.id
                
                mascota_creada = veterinaria.registrar_mascota(
                    email, # Usamos email porque así se definió en veterinaria.py
                    Utils.formatear_nombre(nombre_mascota), 
                    especie, 
                    raza, 
                    fecha_nac
                )

                if mascota_creada:
                    st.success(f"✅ ¡Éxito! Se ha registrado a **{nombre_formateado}** (ID: {cliente_creado.id[:8]}...) y a su mascota **{mascota_creada.nombre}**.")
                    st.balloons()
                else:
                    st.error("⚠️ Mascota no registrada. Podría haber un problema con el ID del cliente o la conexión DB.")

            else:
                st.warning("⚠️ El cliente con este email ya existe. Se intentará registrar la mascota con el cliente existente.")
                
                # Si el cliente ya existe, lo buscamos y registramos la mascota.
                cliente_existente = veterinaria.buscar_cliente(email)
                if cliente_existente:
                     mascota_creada = veterinaria.registrar_mascota(
                        email, 
                        Utils.formatear_nombre(nombre_mascota), 
                        especie, 
                        raza, 
                        fecha_nac
                    )
                     if mascota_creada:
                         st.success(f"✅ Mascota **{mascota_creada.nombre}** registrada al cliente existente: **{cliente_existente.nombre}**.")
                     else:
                         st.error("❌ Error al registrar la mascota. Revise los datos.")
                else:
                    st.error("❌ Error grave: Cliente no se pudo crear y no se encontró el cliente existente.")