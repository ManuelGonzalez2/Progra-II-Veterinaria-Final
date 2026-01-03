import pytest
import sys
import os
from datetime import date
from unittest.mock import MagicMock

# --- 1. CONFIGURACIÓN DEL "SUPER MOCK" ---
# Creamos el actor que fingirá ser Streamlit
mock_streamlit = MagicMock()

# LECCIÓN 1: st.columns (Ya lo teníamos)
def side_effect_columns(spec):
    if isinstance(spec, int):
        return [MagicMock() for _ in range(spec)]
    return [MagicMock() for _ in range(len(spec))]

mock_streamlit.columns.side_effect = side_effect_columns

# LECCIÓN 2: st.tabs (Nuevo!) -> Devuelve una lista de pestañas
def side_effect_tabs(tabs_list):
    return [MagicMock() for _ in tabs_list]

mock_streamlit.tabs.side_effect = side_effect_tabs

# LECCIÓN 3: st.selectbox (Elige siempre el primero)
def side_effect_selectbox(label, options, **kwargs):
    if options:
        return list(options)[0]
    return "Opción Mock"

mock_streamlit.selectbox.side_effect = side_effect_selectbox

# LECCIÓN 4: Inputs de texto y fecha (CRUCIAL PARA TUS ERRORES)
# Hacemos que devuelvan datos reales, no robots.
mock_streamlit.text_input.return_value = "texto_prueba@email.com"  # Un email válido para que pase el regex
mock_streamlit.text_area.return_value = "Descripción de prueba"
mock_streamlit.date_input.return_value = date(2026, 1, 1)        # Una fecha real para SQLite
mock_streamlit.time_input.return_value = "10:00"

# Aplicamos el engaño al sistema
sys.modules["streamlit"] = mock_streamlit
sys.modules["streamlit.components.v1"] = MagicMock()

# --- 2. RUTAS E IMPORTACIONES ---
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(current_dir, '../streamlit')))

# Importamos DB Utils para configurar la base de datos de prueba
import db_utils
from db_utils import create_tables

# Importamos las páginas
try:
    from pages import (
        Gestion_Citas, 
        Historial_Medico, 
        Registrar_Cliente_y_Mascota, 
        Ver_Clientes, 
        Ver_Mascotas
    )
    import Home
except ImportError as e:
    print(f"⚠️ Error importando páginas: {e}")

# --- 3. PREPARACIÓN DE LA BASE DE DATOS (Fixture) ---
# Esto se ejecuta antes de cada test para asegurar que las tablas existen
# y que SQLite no falle al intentar guardar las cosas del Mock.
@pytest.fixture(autouse=True)
def setup_database():
    db_utils.DB_NAME = ":memory:" # Usamos RAM para que sea ultra rápido y no ensucie
    create_tables()

# --- 4. LOS TESTS DE INTERFAZ ---

def test_cargar_home():
    assert Home is not None

def test_ejecutar_gestion_citas():
    try:
        Gestion_Citas.app()
    except Exception as e:
        pytest.fail(f"Fallo en Gestión Citas: {e}")

def test_ejecutar_historial():
    try:
        Historial_Medico.app()
    except Exception as e:
        pytest.fail(f"Fallo en Historial: {e}")

def test_ejecutar_registro():
    try:
        # Al ejecutar esto, usará el "texto_prueba@email.com" que definimos arriba
        Registrar_Cliente_y_Mascota.app()
    except Exception as e:
        pytest.fail(f"Fallo en Registro: {e}")

def test_ejecutar_ver_mascotas():
    try:
        Ver_Mascotas.app()
    except Exception as e:
        pytest.fail(f"Fallo en Ver Mascotas: {e}")

def test_ejecutar_ver_clientes():
    try:
        Ver_Clientes.app()
    except Exception as e:
        pytest.fail(f"Fallo en Ver Clientes: {e}")