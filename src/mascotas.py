# src/mascotas.py
from datetime import date
from .clientes import Cliente 
import uuid # Para generar el ID de la mascota
from .db_connection import get_connection # Para la persistencia
import sqlite3

class Mascota:
    """
    Representa a una mascota, guardando solo el ID del cliente dueño (clave foránea).
    """
    def __init__(self, nombre: str, especie: str, raza: str, fecha_nacimiento: date, 
                 cliente_id: str, id_mascota: str = None):
        
        # 1. ID de la Mascota (Clave Primaria)
        if id_mascota is None:
            self.id = str(uuid.uuid4())
        else:
            self.id = id_mascota

        self.nombre = nombre
        self.especie = especie
        self.raza = raza
        self.fecha_nacimiento = fecha_nacimiento
        
        # 2. Referencia al Dueño (Clave Foránea)
        # Guardamos SOLO el ID del cliente, no el objeto completo.
        self.cliente_id = cliente_id 
        
        # El historial médico es una estructura compleja. 
        # Por ahora, se mantiene en el objeto. Si usáramos BBDD, 
        # habría que guardarlo en una tabla separada.
        self.historial_medico = {
            "vacunas": [],
            "peso": [],
            "observaciones": [],
            "tratamientos": []
        }

    def __str__(self):
        # Ahora mostramos el ID del cliente en lugar del nombre del objeto Cliente
        return f"Mascota: {self.nombre} (Dueño ID: {self.cliente_id[:8]}...)"


# --- FUNCIONES DE PERSISTENCIA (CRUD) ---

def insertar_mascota(mascota: Mascota):
    """Inserta un nuevo objeto Mascota en la tabla 'mascotas' de SQLite."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # La instrucción SQL INSERT
        cursor.execute("""
            INSERT INTO mascotas (id_mascota, nombre, especie, raza, edad, cliente_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            mascota.id, 
            mascota.nombre, 
            mascota.especie, 
            mascota.raza, 
            # SQLite no tiene tipo DATE. Guardamos la fecha como texto (ISO 8601) o calculamos la edad en enteros.
            # Asumo que tu tabla mascotas de db_connection.py usa INTEGER para 'edad', ajusta si es 'fecha_nacimiento'.
            0, # Reemplaza esto con tu lógica de edad o fecha_nacimiento
            mascota.cliente_id # ¡La Clave Foránea!
        ))
        
        conn.commit()
        return True
    
    except sqlite3.IntegrityError:
        # Esto ocurre si el cliente_id no existe en la tabla de clientes (violación de clave foránea)
        print(f"Error: El cliente con ID {mascota.cliente_id} no existe. No se pudo registrar la mascota.")
        return False
        
    except Exception as e:
        print(f"Error al insertar mascota: {e}")
        return False
        
    finally:
        conn.close()