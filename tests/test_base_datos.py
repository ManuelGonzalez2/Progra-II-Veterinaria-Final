import pytest
import sys
import os
import sqlite3
from datetime import date
from unittest.mock import MagicMock

# --- CONFIGURACIÓN DE MOCKS (Streamlit) ---
mock_streamlit = MagicMock()
mock_streamlit.session_state = {"login_correcto": True, "mi_clinica": MagicMock()}
mock_streamlit.text_input.return_value = "test@email.com"
mock_streamlit.text_area.return_value = "Descripción de prueba"
mock_streamlit.date_input.return_value = date(2026, 1, 1)

def side_effect_selectbox(label, options, **kwargs):
    return list(options)[0] if options else "Opción 1"

mock_streamlit.selectbox.side_effect = side_effect_selectbox
mock_streamlit.columns.side_effect = lambda spec: [MagicMock() for _ in range(spec if isinstance(spec, int) else len(spec))]
mock_streamlit.tabs.side_effect = lambda tabs_list: [MagicMock() for _ in tabs_list]

sys.modules["streamlit"] = mock_streamlit

# --- CONFIGURACIÓN DE RUTAS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(current_dir, '..'))) # Raíz para src
sys.path.append(os.path.abspath(os.path.join(current_dir, '../streamlit'))) # Para páginas

import db_utils
from db_utils import create_tables

# Importamos las clases de lógica para subir COBERTURA
from src.veterinaria import Veterinaria
from src.clientes import Cliente
from src.mascotas import Mascota
from src.citas import Cita
from src.utils import Utils

try:
    from pages import Gestion_Citas, Historial_Medico, Registrar_Cliente_y_Mascota, Ver_Clientes, Ver_Mascotas
    import Home
except ImportError as e:
    print(f"⚠️ Error importando páginas: {e}")

# --- WRAPPER DE CONEXIÓN ---
class ConnWrapper:
    def __init__(self, real_conn): self.real_conn = real_conn
    def close(self): pass # Evita que la app cierre la DB en memoria
    def __getattr__(self, name): return getattr(self.real_conn, name)

@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    real_conn = sqlite3.connect(":memory:", check_same_thread=False)
    safe_conn = ConnWrapper(real_conn)
    monkeypatch.setattr(db_utils, "get_connection", lambda: safe_conn)
    create_tables()
    yield 
    real_conn.close()

# ==========================================================
# 1. NUEVOS TESTS DE LÓGICA (PARA SUBIR COBERTURA DE SRC)
# ==========================================================

def test_logica_clases_principales():
    """Este test dispara la cobertura de veterinaria, clientes y mascotas"""
    # Test Veterinaria (Singleton y métodos)
    clinica = Veterinaria()
    clinica.inicializar() # Sube % en veterinaria.py
    
    # Test Clientes y Mascotas
    propietario = Cliente(nombre="Juan Perro", telefono="666", email="juan@test.com")
    animal = Mascota(nombre="Rex", especie="Perro", raza="German Shepherd", edad=3)
    
    propietario.anadir_mascota(animal) # Sube % en clientes.py y mascotas.py
    assert len(propietario.mascotas) == 1
    assert animal.nombre == "Rex"

def test_logica_citas_y_utils():
    """Sube la cobertura de citas.py y utils.py"""
    cita = Cita(id_mascota=1, fecha="2026-01-01", hora="10:00", motivo="Vacuna")
    assert cita.motivo == "Vacuna"
    
    assert Utils.validar_email("correo@valido.com") is True
    assert Utils.validar_email("correo-invalido") is False

# ==========================================================
# 2. TESTS DE INTERFAZ (LOS QUE YA TENÍAS)
# ==========================================================

def test_cargar_home():
    assert Home is not None

def test_ejecutar_paginas_streamlit():
    """Ejecuta todas las páginas para asegurar que no hay NameErrors ni fallos de importación"""
    paginas = [Gestion_Citas, Historial_Medico, Registrar_Cliente_y_Mascota, Ver_Clientes, Ver_Mascotas]
    for pagina in paginas:
        try:
            pagina.app()
        except Exception as e:
            pytest.fail(f"La página {pagina.__name__} falló: {e}")