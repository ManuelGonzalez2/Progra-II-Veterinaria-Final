import streamlit as st
import pandas as pd
from db_utils import read_query

st.set_page_config(page_title="Listado de Pacientes", page_icon="🐾", layout="wide")

def app():
    st.title("🐾 Listado de Pacientes")
    st.caption("Inventario completo de mascotas registradas en la base de datos.")


    query = """
        SELECT nombre, especie, raza, fecha_nacimiento, propietario, telefono, email 
        FROM pacientes
    """
    datos = read_query(query)

    if not datos:
        st.info(" No hay mascotas registradas todavía. Ve a 'Registrar Cliente' para añadir la primera.")
        return

    # Convertimos los datos crudos a un DataFrame de Pandas
    df = pd.DataFrame(datos, columns=[
        "Nombre Mascota", 
        "Especie", 
        "Raza", 
        "Fecha Nacimiento", 
        "Dueño", 
        "Teléfono", 
        "Email"
    ])

    # Filtros de Búsqueda 
    st.subheader("🔍 Buscador y Filtros")
    
    col_search, col_filter = st.columns([3, 1])
    
    with col_search:
        # Busca texto en cualquier columna
        search_term = st.text_input("Buscar por Nombre, Raza o Dueño", placeholder="Ej: Toby, Pastor Alemán, Juan...", key="search_mascota")
        
        if search_term:
            # Conviertimos toda la fila a texto y buscamos la palabra clave
            mask = df.apply(lambda row: search_term.lower() in row.astype(str).str.lower().to_string(), axis=1)
            df = df[mask]
    
    with col_filter:
        # Filtro por Especie (Dinámico: solo muestra las especies que existen en la DB)
        lista_especies = ['Todas'] + sorted(df['Especie'].unique().tolist())
        selected_especie = st.selectbox("Filtrar por Especie", lista_especies)
        
        if selected_especie != 'Todas':
            df = df[df['Especie'] == selected_especie]


    st.divider()
    
    # Métrica de resumen
    st.metric(label="Total de Pacientes Filtrados", value=len(df))
    
    # Mostramos la tabla bonita
    st.dataframe(
        df, 
        use_container_width=True,
        hide_index=True,
        column_config={
            "Email": st.column_config.TextColumn("Email", help="Email del propietario"),
            "Fecha Nacimiento": st.column_config.DateColumn("Nacimiento", format="DD/MM/YYYY")
        }
    )

if __name__ == "__main__":
    app()