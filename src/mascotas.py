import uuid #Para generar un ID unico y aleatorio
import sqlite3 #Para mirar en la BBDD si un cliente esta repetido por ej.
from datetime import date
from .db_connection import get_connection

class Mascota:
    def __init__(self, nombre: str, especie: str, raza: str, fecha_nacimiento: date, 
                 cliente_id: str, id_mascota: str = None):
        
        # Creamos el ID de la Mascota (Clave Primaria)
        if id_mascota is None:
            self.id = str(uuid.uuid4())
        else:
            self.id = id_mascota

        self.nombre = nombre
        self.especie = especie
        self.raza = raza
        self.fecha_nacimiento = fecha_nacimiento
        
        # Creamos la foreing key
        self.cliente_id = cliente_id 
        
        # Historial médico (diccionario en memoria)
        self.historial_medico = {
            "vacunas": [],
            "peso": [],
            "observaciones": [],
            "tratamientos": []
        }

    def __str__(self):
        return f"Mascota: {self.nombre} (Dueño ID: {self.cliente_id[:8]}...)"


def registrar_mascota_db(mascota: Mascota):
    #Inserta un nuevo objeto Mascota en la tabla 'mascotas' de SQLite.
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Convertimos la fecha a string para SQLite (formato YYYY-MM-DD)
        fecha_str = str(mascota.fecha_nacimiento)

        cursor.execute(
            mascota.id, 
            mascota.nombre, 
            mascota.especie, 
            mascota.raza, 
            fecha_str, # Guardamos la fecha como texto
            mascota.cliente_id 
        )
        
        conn.commit()
        return True
    
    except sqlite3.IntegrityError:
        # Esto ocurre si el cliente_id no existe en la tabla de clientes
        print(f"Error: El cliente con ID {mascota.cliente_id} no existe.")
        return False
        
    except Exception as e:
        print(f"Error al insertar mascota: {e}")
        return False
        
    finally:
        conn.close()