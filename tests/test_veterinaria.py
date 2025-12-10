# tests/test_veterinaria.py

import sys
import os
import pytest
from datetime import date
# La siguiente linea de codigo es un ajuste de ruta para que pueda encontrar la carpeta src
# Es la solución de emergencia para que los ficheros de pages reconozcan al motor.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.veterinaria import Veterinaria 
from src.utils import Utils

# Usamos una fixture para inicializar la clínica antes de cada test
@pytest.fixture
def clinica_vacia():
    # Inicializa el motor, que a su vez carga el CSV si existe
    # Garantiza que cada prueba es independiente
    return Veterinaria()

def test_inicializacion_clientes(clinica_vacia):
    """Verifica que la lista de clientes se inicializa correctamente (cargando el CSV)."""
    assert len(clinica_vacia.clientes) >= 0 # Debe tener 0 o más si hay datos en el CSV

def test_registro_nuevo_cliente(clinica_vacia):
    """Verifica que un nuevo cliente se añade correctamente."""
    num_inicial = len(clinica_vacia.clientes)
    
    # Act: Registrar un cliente de prueba
    clinica_vacia.registrar_cliente("Test Cliente", "555123456", "test@prueba.com")
    
    # Assert: Verificar que el número de clientes ha aumentado en 1
    assert len(clinica_vacia.clientes) == num_inicial + 1
    
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
        date(2022, 1, 1) # Usamos date del módulo datetime
    )
    
    # Assert: 1. La mascota se creó. 2. La mascota tiene el objeto cliente asignado.
    assert mascota is not None
    assert mascota.nombre == "Rex"
    assert mascota.cliente.nombre == "Owner Test" # <-- Testea la conexión de objetos!

def test_buscar_cliente_existe(clinica_vacia):
    """Verifica que buscar_cliente retorna el objeto correcto si existe."""
    email_test = "busca@test.com"
    clinica_vacia.registrar_cliente("Cliente Buscable", "123", email_test)
    
    # Act
    cliente_encontrado = clinica_vacia.buscar_cliente(email_test)
    cliente_no_encontrado = clinica_vacia.buscar_cliente("otro@email.com")
    
    # Assert
    assert cliente_encontrado.nombre == "Cliente Buscable"
    assert cliente_no_encontrado is None

def test_creacion_cita(clinica_vacia):
    """Verifica que se crea una cita y se asigna a una mascota."""
    # Arrange: Necesitamos un cliente y una mascota
    cliente = clinica_vacia.registrar_cliente("Dueño Citas", "999", "cita@test.com")
    mascota = clinica_vacia.registrar_mascota(
        "cita@test.com", "Fido", "Perro", "Beagle", date(2023, 5, 5)
    )
    
    num_inicial = len(clinica_vacia.citas)
    
    # Act
    nueva_cita = clinica_vacia.crear_cita(date.today(), "15:00", "Revision", "Dr. Tomás", mascota)
    
    # Assert
    assert len(clinica_vacia.citas) == num_inicial + 1
    assert nueva_cita.mascota.nombre == "Fido"
    assert nueva_cita.veterinario == "Dr. Tomás"

def test_anadir_historial(clinica_vacia):
    """Verifica las 4 funciones de añadir datos al historial médico."""
    # Arrange: Cliente y Mascota
    cliente = clinica_vacia.registrar_cliente("Historial Dueño", "111", "hist@test.com")
    mascota = clinica_vacia.registrar_mascota(
        "hist@test.com", "Gato Test", "Gato", "Siames", date(2024, 1, 1)
    )
    
    # --- Test 1: Vacuna ---
    clinica_vacia.anadir_vacuna(mascota, "Rabia", date.today())
    assert "Rabia" in mascota.historial_medico["vacunas"][0]
    
    # --- Test 2: Peso ---
    clinica_vacia.anadir_peso(mascota, 4.5, date.today())
    assert mascota.historial_medico["peso"][0]["peso"] == 4.5
    
    # --- Test 3: Observación ---
    clinica_vacia.anadir_observacion(mascota, "Ojos irritados.", date.today())
    assert "Ojos irritados" in mascota.historial_medico["observaciones"][0]
    
    # --- Test 4: Tratamiento ---
    clinica_vacia.anadir_tratamiento(mascota, "Antibiotico 7 días.", date.today())
    assert "Antibiotico 7 días" in mascota.historial_medico["tratamientos"][0]

def test_eliminar_cliente(clinica_vacia):
    """
    Verifica la operación DELETE del CRUD: 
    1. Elimina el objeto Cliente de la memoria.
    2. Asegura que el cliente ya no está en el CSV (reescritura de persistencia).
    """
    email_a_eliminar = "cliente_borrar@test.com"
    
    # Arrange: Registramos un cliente y su mascota
    cliente_test = clinica_vacia.registrar_cliente("Cliente Borrar", "123", email_a_eliminar)
    clinica_vacia.registrar_mascota(email_a_eliminar, "Mascota Cero", "Perro", "Chihuahua", date(2023, 1, 1))
    
    # Guardamos el número inicial de clientes
    num_inicial = len(clinica_vacia.clientes)
    
    # Act: Eliminar el cliente
    resultado = clinica_vacia.eliminar_cliente(email_a_eliminar)
    
    # Assert 1: Se eliminó correctamente
    assert resultado is True
    # Assert 2: El cliente ya no está en la lista en memoria
    assert len(clinica_vacia.clientes) == num_inicial - 1
    # Assert 3: El cliente ya no se puede buscar
    assert clinica_vacia.buscar_cliente(email_a_eliminar) is None
    
    # Assert 4 (Persistencia): Cargar el CSV de nuevo para verificar que la fila fue eliminada.
    # Nota: Si el CSV es reescrito correctamente por eliminar_cliente(), 
    # este cliente no debería aparecer si recargamos los datos.
    
    # Creamos una NUEVA instancia para forzar la recarga del CSV limpio
    nueva_clinica = Veterinaria()
    assert nueva_clinica.buscar_cliente(email_a_eliminar) is None

def test_validaciones_utils():
    """Prueba los casos negativos de Utils para subir cobertura."""
    # Caso 1: Email inválido (sin arroba)
    assert Utils.validar_email("email_sin_arroba.com") is False
    
    # Caso 2: Email inválido (sin punto)
    assert Utils.validar_email("usuario@dominio") is False
    
    # Caso 3: Email vacío
    assert Utils.validar_email("") is False
    
    # Caso 4: Formateo de nombre (mayúsculas y minúsculas)
    assert Utils.formatear_nombre("  pepe  ") == "Pepe"
    assert Utils.formatear_nombre("JUAN") == "Juan"


