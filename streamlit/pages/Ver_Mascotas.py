import sys
import os
# Ajuste de ruta para que pueda encontrar la carpeta src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import streamlit as st
import pandas as pd
from src.veterinaria import Veterinaria

# --- Configuración de la Página de Streamlit ---
st.set_page_config(page_title="Listado de Pacientes", page_icon="🐾", layout="wide")

# Inicialización de la clase Veterinaria (Singleton)
if "mi_clinica" not in st.session_state:
    st.session_state["mi_clinica"] = Veterinaria()

# Control de acceso
if "login_correcto" not in st.session_state or not st.session_state["login_correcto"]:
    st.warning("🔒 Debes iniciar sesión para acceder al listado de pacientes.")
    st.stop()

st.title("🐾 Listado de Pacientes")
st.caption("Inventario completo de mascotas y sus dueños.")

veterinaria = st.session_state["mi_clinica"]

lista_mascotas = []
# Aplanamos la lista de mascotas para la visualización en Streamlit
for cliente in veterinaria.clientes:
    for mascota in cliente.mascotas:
        lista_mascotas.append({
            # Incluimos el ID de la mascota (clave primaria de SQLite)
            "ID Paciente": mascota.id[:8] + "...", 
            "Nombre Mascota": mascota.nombre,
            "Especie": mascota.especie,
            "Raza": mascota.raza,
            # Formateo de fecha para mejor visualización
            "Fecha Nacimiento": mascota.fecha_nacimiento.strftime('%d/%m/%Y'),
            "Dueño": cliente.nombre,  
            "Contacto Dueño": cliente.telefono
        })

if not lista_mascotas:
    st.info("ℹ️ No hay mascotas registradas todavía.")
else:
    df = pd.DataFrame(lista_mascotas)
    
    # --- 1. Filtros Rápidos (Mejora de "Gracia") ---
    st.subheader("Filtros de Búsqueda")
    
    col_search, col_filter = st.columns([3, 1])
    
    with col_search:
        # Búsqueda por palabra clave en cualquier campo
        search_term = st.text_input("Buscar por Nombre, Raza o Dueño", key="search_mascota")
        if search_term:
            df = df[
                df.apply(lambda row: search_term.lower() in row.astype(str).str.lower().to_string(), axis=1)
            ]
            st.caption(f"Mostrando {len(df)} resultados.")
    
    with col_filter:
        # Filtro por Especie
        especies_unicas = ['Todos'] + sorted(df['Especie'].unique().tolist())
        selected_especie = st.selectbox("Filtrar por Especie", especies_unicas)
        
        if selected_especie != 'Todos':
            df = df[df['Especie'] == selected_especie]


    # --- 2. Visualización de Datos ---
    st.divider()
    
    # Usamos st.metric para un resumen visual
    total_mascotas = len(df)
    st.metric(label="Total de Pacientes", value=total_mascotas, delta=None)
    
    st.dataframe(
        df, 
        use_container_width=True,
        hide_index=True,
        # Ocultamos el ID en el dataframe, pero es bueno tenerlo en los datos.
        column_order=("Nombre Mascota", "Especie", "Raza", "Fecha Nacimiento", "Dueño", "Contacto Dueño")
    )