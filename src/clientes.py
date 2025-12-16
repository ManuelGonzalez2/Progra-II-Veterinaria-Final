import uuid
import sqlite3
from datetime import date, datetime
from .db_connection import get_connection

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
        self.mascotas = [] # Lista de objetos Mascota

    def __str__(self):
        return f"Cliente ID: {self.id[:8]}... | Nombre: {self.nombre} | Email: {self.email}"


# --- FUNCIONES DE PERSISTENCIA (CRUD) ---

def registrar_cliente_db(cliente: Cliente):
    """Inserta un nuevo objeto Cliente en la tabla 'clientes' de SQLite."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Instrucción SQL ajustada a los atributos reales de la clase
        cursor.execute("""
            INSERT INTO clientes (id_cliente, nombre, email, telefono)
            VALUES (?, ?, ?, ?)
        """, (
            cliente.id, 
            cliente.nombre, 
            cliente.email, 
            cliente.telefono
        ))
        
        conn.commit()
        return True
    
    except sqlite3.IntegrityError:
        print(f"Error: El cliente con ID {cliente.id} o email {cliente.email} ya existe.")
        return False
    except Exception as e:
        print(f"Error al insertar cliente: {e}")
        return False
    finally:
        conn.close()

def eliminar_cliente_db(id_cliente):
    """Elimina un cliente de la BBDD por ID."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Gracias al ON DELETE CASCADE, esto borrará también mascotas y citas
        cursor.execute("DELETE FROM clientes WHERE id_cliente = ?", (id_cliente,))
        
        if cursor.rowcount > 0:
            conn.commit()
            return True
        return False
        
    except Exception as e:
        print(f"Error al eliminar cliente de DB: {e}")
        return False
    finally:
        conn.close()

def cargar_clientes_db():
    """
    Recupera todos los clientes de la BBDD y también sus mascotas asociadas.
    Devuelve una lista de objetos Cliente.
    """
    conn = get_connection()
    cursor = conn.cursor()
    lista_clientes = []
    
    try:
        # 1. Seleccionar todos los clientes
        cursor.execute("SELECT id_cliente, nombre, email, telefono FROM clientes")
        rows = cursor.fetchall()
        
        # Importación LOCAL para evitar el error de 'Importación Circular'
        # Esto es un truco necesario porque mascota.py importa cliente.py
        from .mascotas import Mascota 

        for row in rows:
            id_cli, nombre, email, telefono = row
            cliente_obj = Cliente(nombre, telefono, email, id_cli)
            
            # 2. Para cada cliente, buscamos sus mascotas en la BBDD
            # Hacemos una segunda consulta filtrando por cliente_id
            cursor.execute("""
                SELECT id_mascota, nombre, especie, raza, fecha_nacimiento 
                FROM mascotas WHERE cliente_id = ?
            """, (id_cli,))
            
            mascotas_rows = cursor.fetchall()
            
            for m_row in mascotas_rows:
                id_masc, m_nom, m_esp, m_raza, m_fecha_str = m_row
                
                # Convertir la fecha de string (SQLite) a objeto date (Python)
                try:
                    fecha_nac = datetime.strptime(m_fecha_str, '%Y-%m-%d').date()
                except ValueError:
                    fecha_nac = date.today() # Fallback si la fecha está mal
                
                # Creamos el objeto Mascota y lo añadimos a la lista del cliente
                mascota_obj = Mascota(m_nom, m_esp, m_raza, fecha_nac, id_cli, id_masc)
                
                # Cargar historial médico (Opcional: JSON parse si lo implementaste)
                # mascota_obj.historial_medico = ... 
                
                cliente_obj.mascotas.append(mascota_obj)
            
            lista_clientes.append(cliente_obj)
            
    except Exception as e:
        print(f"Error cargando clientes: {e}")
    finally:
        conn.close()
        
    return lista_clientes