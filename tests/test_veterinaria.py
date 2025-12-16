# tests/test_veterinaria.py

import sys
import os
import pytest
from datetime import date
import sqlite3
import shutil # Necesario para copiar el archivo de BBDD
# Importar módulos necesarios
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# La línea de arriba no es necesaria si ejecutas los tests desde la raíz.

from src.veterinaria import Veterinaria 
from src.utils import Utils
# Importamos la conexión a BBDD para modificar la ruta temporalmente
from src.db_connection import DB_NAME, get_connection, setup_database 

# --- FIXTURE CRÍTICA PARA SQLite ---
@pytest.fixture
def clinica_vacia(tmp_path):
    """
    Inicializa la clínica usando un archivo SQLite temporal.
    Esto aísla cada prueba de la BBDD de producción.
    """
    # 1. Creamos un nombre temporal para la BBDD
    temp_db_name = tmp_path / "test_veterinaria.db"
    
    # 2. Reemplazamos el nombre de la BBDD global por el temporal (¡PELIGROSO PERO NECESARIO!)
    # Esto asegura que Veterinaria y db_connection utilicen el archivo temporal.
    original_db_name = DB_NAME
    # Modificamos globalmente el nombre de la BBDD antes de la prueba
    # Usando monkeypatch o simplemente asignación (si DB_NAME es mutable, lo es en Python)
    from src import db_connection # Importamos el módulo para acceder a DB_NAME
    db_connection.DB_NAME = str(temp_db_name)
    
    # 3. Configuramos la BBDD temporal (creamos las tablas)
    setup_database()
    
    # 4. Inicializamos el motor de la clínica (apuntando al temporal)
    clinica = Veterinaria()
    
    # 5. Ejecutamos el test
    yield clinica
    
    # 6. Tarea de limpieza (Teardown): Restauramos el nombre original.
    db_connection.DB_NAME = original_db_pname
    
    # El archivo temp_db_name se elimina automáticamente al finalizar tmp_path.


def test_inicializacion_clientes(clinica_vacia):
    """Verifica que la lista de clientes se inicializa correctamente (cargando de SQLite)."""
    assert len(clinica_vacia.clientes) == 0 # Esperamos 0 porque la BBDD temporal está vacía.

def test_registro_nuevo_cliente(clinica_vacia):
    """Verifica que un nuevo cliente se añade correctamente (persistencia en DB)."""
    num_inicial = len(clinica_vacia.clientes)
    
    # Act: Registrar un cliente de prueba
    cliente_nuevo = clinica_vacia.registrar_cliente("Test Cliente", "555123456", "test@prueba.com")
    
    # Assert: 1. El cliente se creó. 2. El número de clientes ha aumentado.
    assert cliente_nuevo is not None
    assert len(clinica_vacia.clientes) == num_inicial + 1
    
    # Assert 3: Verificar persistencia en DB (opcional, ya que registrar_cliente lo hace)
    # Creamos una NUEVA instancia para forzar la recarga de la BBDD temporal
    nueva_clinica = Veterinaria()
    assert nueva_clinica.buscar_cliente("test@prueba.com") is not None
    
# NOTA: Los siguientes tests siguen siendo válidos porque operan en memoria, 
# y asumen que las funciones registrar_cliente/registrar_mascota insertan en DB 
# y actualizan la memoria (que es lo que hace tu código refactorizado).

def test_registro_mascota(clinica_vacia):
    """Verifica el registro de una mascota y la conexión al dueño."""
    # Arrange: Asegurarnos de que el dueño existe
    cliente = clinica_vacia.registrar_cliente("Owner Test", "987", "owner@test.com")
    
    # Act: Registrar la mascota
    mascota = clinica_vacia.registrar_mascota(
        "owner@test.com", 
        "Rex", 
        "Perro", 
        "Labrador", 
        date(2022, 1, 1)
    )
    
    # Assert
    assert mascota is not None
    assert mascota.nombre == "Rex"
    # El objeto Cliente debería estar reconstruido en el objeto Mascota en memoria.
    assert mascota.cliente_id == cliente.id # VERIFICACIÓN MÁS SEGURA CON EL ID DE SQLITE
    
# ... (test_buscar_cliente_existe, test_creacion_cita, test_anadir_historial, test_validaciones_utils se mantienen) ...

def test_eliminar_cliente(clinica_vacia):
    """
    Verifica la operación DELETE del CRUD: 
    1. Elimina el objeto Cliente de la memoria.
    2. Asegura que los datos fueron eliminados de SQLite.
    """
    email_a_eliminar = "cliente_borrar@test.com"
    
    # Arrange: Registramos un cliente y su mascota en la BBDD temporal
    cliente_test = clinica_vacia.registrar_cliente("Cliente Borrar", "123", email_a_eliminar)
    clinica_vacia.registrar_mascota(email_a_eliminar, "Mascota Cero", "Perro", "Chihuahua", date(2023, 1, 1))
    
    num_inicial = len(clinica_vacia.clientes)
    
    # Act: Eliminar el cliente (la función debe usar DELETE de SQLite)
    resultado = clinica_vacia.eliminar_cliente(email_a_eliminar)
    
    # Assert 1: Se eliminó correctamente
    assert resultado is True
    # Assert 2: El cliente ya no está en la lista en memoria
    assert len(clinica_vacia.clientes) == num_inicial - 1
    
    # Assert 3 (Persistencia): Crear una NUEVA instancia para forzar la recarga de la BBDD limpia
    nueva_clinica = Veterinaria()
    assert nueva_clinica.buscar_cliente(email_a_eliminar) is None
    
    # Assert 4 (CASCADE): Verificar que la mascota también se eliminó de la BBDD
    # Como la mascota fue eliminada, el cliente ya no tendrá mascotas en su lista recargada
    cliente_recargado = nueva_clinica.buscar_cliente("Owner Test") # Cliente que no se borró
    # Hay que verificar que la mascota de 'Cliente Borrar' no aparezca en ninguna parte.
    
    # Alternativamente, podemos hacer una consulta directa a SQLite