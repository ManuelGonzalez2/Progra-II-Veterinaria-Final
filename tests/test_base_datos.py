import pytest
import sys
import os
import sqlite3
from datetime import date
from unittest.mock import MagicMock

# ==========================================
# 1. CONFIGURACIÓN DEL SUPER-MOCK (Interfaz)
# ==========================================

mock_streamlit = MagicMock()

# --- Session State ---
mock_streamlit.session_state = {
    "login_correcto": True,
    "mi_clinica": MagicMock()
}

# --- Inputs y Datos ---
mock_streamlit.text_input.return_value = "test@email.com"
mock_streamlit.sidebar.text_input.return_value = "test@email.com"
mock_streamlit.text_area.return_value = "Descripción de prueba"
mock_streamlit.date_input.return_value = date(2026, 1, 1)

# --- Selectores ---
def side_effect_selectbox(label, options, **kwargs):
    if options and isinstance(options, (list, tuple)):
        return list(options)[0]
    return "Opción 1"

mock_streamlit.selectbox.side_effect = side_effect_selectbox
mock_streamlit.sidebar.selectbox.side_effect = side_effect_selectbox
mock_streamlit.sidebar.radio.return_value = "Inicio"

# --- Layouts ---
def side_effect_columns(spec):
    count = spec if isinstance(spec, int) else len(spec)
    return [MagicMock() for _ in range(count)]

mock_streamlit.columns.side_effect = side_effect_columns

def side_effect_tabs(tabs_list):
    return [MagicMock() for _ in tabs_list]

mock_streamlit.tabs.side_effect = side_effect_tabs

# Inyectar Mock
sys.modules["streamlit"] = mock_streamlit
sys.modules["streamlit.components.v1"] = MagicMock()


# ==========================================
# 2. RUTAS E IMPORTACIONES
# ==========================================
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(current_dir, '../streamlit')))

import db_utils
from db_utils import create_tables, run_query

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


# ==========================================
# 3. EL "GUARDAESPALDAS" DE LA CONEXIÓN 🛡️
# ==========================================

class ConnWrapper:
    """
    Esta clase envuelve la conexión real. 
    Deja pasar todo (execute, commit, cursor) MENOS el close.
    """
    def __init__(self, real_conn):
        self.real_conn = real_conn
    
    def close(self):
        # ¡AQUÍ ESTÁ EL TRUCO! No hacemos nada.
        pass
    
    def cursor(self):
        return self.real_conn.cursor()
    
    def commit(self):
        return self.real_conn.commit()
    
    def execute(self, sql, params=()):
        return self.real_conn.execute(sql, params)
        
    def __getattr__(self, name):
        # Para cualquier otra cosa, se lo pasamos a la conexión real
        return getattr(self.real_conn, name)

@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """
    Crea una base de datos en memoria y usa el Wrapper para evitar
    que el código de la app la cierre antes de tiempo.
    """
    # 1. Creamos la conexión real
    real_conn = sqlite3.connect(":memory:", check_same_thread=False)
    
    # 2. Creamos al guardaespaldas
    safe_conn = ConnWrapper(real_conn)
    
    # 3. Obligamos a db_utils a usar al guardaespaldas
    monkeypatch.setattr(db_utils, "get_connection", lambda: safe_conn)
    
    # 4. Configuramos la DB (Tablas y Datos)
    create_tables()
    
    # Insertamos Paciente de prueba usando la conexión real
    c = real_conn.cursor()
    c.execute("""
        INSERT INTO pacientes (nombre, especie, raza, fecha_nacimiento, propietario, telefono, email)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ("Simba Test", "Perro", "Labrador", "2020-01-01", "Dueño Test", "600000000", "test@email.com"))
    real_conn.commit()

    # --- AQUÍ EMPIEZA EL TEST ---
    yield 
    # --- AQUÍ TERMINA EL TEST ---

    # 5. Cerramos de verdad al final de todo
    real_conn.close()


# ==========================================
# 4. EJECUCIÓN DE TESTS
# ==========================================

def test_cargar_home():
    assert Home is not None

def test_ejecutar_gestion_citas():
    try:
        Gestion_Citas.app()
    except Exception as e:
        pytest.fail(f"Gestión Citas falló: {e}")

def test_ejecutar_historial():
    try:
        Historial_Medico.app()
    except Exception as e:
        pytest.fail(f"Historial falló: {e}")

def test_ejecutar_registro():
    try:
        Registrar_Cliente_y_Mascota.app()
    except Exception as e:
        pytest.fail(f"Registro falló: {e}")

def test_ejecutar_ver_mascotas():
    try:
        Ver_Mascotas.app()
    except Exception as e:
        pytest.fail(f"Ver Mascotas falló: {e}")

def test_ejecutar_ver_clientes():
    try:
        Ver_Clientes.app()
    except Exception as e:
        pytest.fail(f"Ver Clientes falló: {e}")