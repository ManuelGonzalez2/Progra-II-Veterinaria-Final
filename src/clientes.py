from datetime import date 
import uuid # Necesitamos esta librería para generar IDs únicos
from .db_connection import get_connection # Importamos la conexión a SQLite
import sqlite3 # Necesitamos el manejador de errores de SQLite

class Cliente:
    def __init__(self, nombre: str, telefono: str, email: str, id_cliente: str = None):
        
        # 1. Generación del ID Único (Clave Primaria)
        # Si no se pasa un ID (es un cliente nuevo), se genera uno.
        if id_cliente is None:
            self.id = str(uuid.uuid4())
        else:
            self.id = id_cliente
            
        self.nombre = nombre
        self.telefono = telefono
        self.email = email
        self.mascotas = [] # Lista de objetos Mascota (se cargará al iniciar)

    def __str__(self):
        # Incluimos el ID en la representación
        return f"Cliente ID: {self.id[:8]}... | Nombre: {self.nombre} | Email: {self.email}"


# --- FUNCIONES DE PERSISTENCIA (CRUD) ---

def insertar_cliente(cliente: Cliente):
    """Inserta un nuevo objeto Cliente en la tabla 'clientes' de SQLite."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # La instrucción SQL INSERT con todos los campos
        cursor.execute("""
            INSERT INTO clientes (id_cliente, nombre, apellido, email, telefono)
            VALUES (?, ?, ?, ?, ?)
        """, (
            cliente.id, 
            cliente.nombre, 
            "", # Asumo que el apellido no lo tienes en el init, por lo que ponemos cadena vacía.
            cliente.email, 
            cliente.telefono
        ))
        
        conn.commit() # Guardamos los cambios
        return True
    
    except sqlite3.IntegrityError:
        # Ocurre si el ID o el EMAIL ya existen (violación de UNIQUE)
        print(f"Error: El cliente con ID {cliente.id} o email {cliente.email} ya existe.")
        return False
        
    except Exception as e:
        print(f"Error al insertar cliente: {e}")
        return False
        
    finally:
        conn.close() # Siempre cerramos la conexión
        
def eliminar_cliente_db(id_cliente):
    """Elimina un cliente de la BBDD por ID."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # La tabla mascotas tiene ON DELETE CASCADE, por lo que las mascotas se eliminan automáticamente.
        cursor.execute("DELETE FROM clientes WHERE id_cliente = ?", (id_cliente,))
        
        if cursor.rowcount > 0:
            conn.commit()
            conn.close()
            return True # Eliminación exitosa
        
        conn.close()
        return False # Cliente no encontrado
        
    except Exception as e:
        print(f"Error al eliminar cliente de DB: {e}")
        conn.close()
        return False