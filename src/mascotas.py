import uuid
import sqlite3
from datetime import date
from .db_connection import get_connection

class Mascota:
    """
    Representa a una mascota, guardando el ID del cliente dueño (clave foránea).
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
        self.cliente_id = cliente_id 
        
        # Historial médico (diccionario en memoria)
        # Nota: En una BBDD real compleja, esto sería otra tabla 'historial'.
        # Aquí lo mantenemos en memoria o se podría guardar como JSON text en SQLite.
        self.historial_medico = {
            "vacunas": [],
            "peso": [],
            "observaciones": [],
            "tratamientos": []
        }

    def __str__(self):
        return f"Mascota: {self.nombre} (Dueño ID: {self.cliente_id[:8]}...)"


# --- FUNCIONES DE PERSISTENCIA (CRUD) ---

def registrar_mascota_db(mascota: Mascota):
    """Inserta un nuevo objeto Mascota en la tabla 'mascotas' de SQLite."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Convertimos la fecha a string para SQLite (formato YYYY-MM-DD)
        fecha_str = str(mascota.fecha_nacimiento)

        # La instrucción SQL INSERT
        cursor.execute("""
            INSERT INTO mascotas (id_mascota, nombre, especie, raza, fecha_nacimiento, cliente_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            mascota.id, 
            mascota.nombre, 
            mascota.especie, 
            mascota.raza, 
            fecha_str, # Guardamos la fecha como texto
            mascota.cliente_id # ¡La Clave Foránea!
        ))
        
        conn.commit()
        return True
    
    except sqlite3.IntegrityError:
        # Esto ocurre si el cliente_id no existe en la tabla de clientes
        print(f"Error FK: El cliente con ID {mascota.cliente_id} no existe.")
        return False
        
    except Exception as e:
        print(f"Error al insertar mascota: {e}")
        return False
        
    finally:
        conn.close()