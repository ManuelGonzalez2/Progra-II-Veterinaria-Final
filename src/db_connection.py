import sqlite3
import os

# 1. Definimos el nombre del archivo de la BBDD
DB_NAME = 'veterinaria.db'

def setup_database():
    """
    Establece la conexión a SQLite y asegura que las tablas
    necesarias (clientes, mascotas) existan.
    """
    # Conexión: Si el archivo no existe, lo crea.
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 2. Creamos la tabla de Clientes
    # Usamos id_cliente como clave primaria
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id_cliente TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            apellido TEXT,
            email TEXT UNIQUE,
            telefono TEXT
        )
    """)

    # 3. Creamos la tabla de Mascotas
    # Aquí es clave la CLAVE FORÁNEA (cliente_id) para relacionarla con Clientes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mascotas (
            id_mascota TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            especie TEXT,
            raza TEXT,
            edad INTEGER,
            cliente_id TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id_cliente)
                ON DELETE CASCADE
        )
    """)

    # Puedes añadir más tablas (citas, historial) aquí si lo necesitas
    
    # 4. Guardamos los cambios y cerramos la conexión
    conn.commit()
    conn.close()
    
    # Devolvemos un mensaje para saber si la conexión fue exitosa
    return f"Conexión a '{DB_NAME}' establecida y tablas aseguradas."

def get_connection():
    """Devuelve una nueva conexión a la base de datos para usar en CRUD."""
    return sqlite3.connect(DB_NAME)

# Llamada inicial para configurar la BBDD
# Esto solo crea las tablas la primera vez que se ejecuta.
if __name__ == '__main__':
    print(setup_database())