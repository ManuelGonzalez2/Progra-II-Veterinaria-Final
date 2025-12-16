import sqlite3
import os

# 1. Definimos el nombre del archivo de la BBDD
DB_NAME = 'veterinaria.db'

def setup_database():
    """
    Establece la conexión a SQLite y asegura que las tablas
    necesarias (clientes, mascotas, citas) existan.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 2. Tabla de Clientes
    # id_cliente es la CLAVE PRIMARIA
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id_cliente TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            apellido TEXT,
            email TEXT UNIQUE,  
            telefono TEXT
        )
    """)

    # 3. Tabla de Mascotas
    # id_mascota es la CLAVE PRIMARIA
    # cliente_id es la CLAVE FORÁNEA (relación 1-a-Muchos)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mascotas (
            id_mascota TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            especie TEXT,
            raza TEXT,
            fecha_nacimiento TEXT, -- Guardamos la fecha como texto 'YYYY-MM-DD'
            cliente_id TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id_cliente)
                ON DELETE CASCADE -- Si se borra el cliente, se borran sus mascotas
        )
    """)
    
    # 4. Tabla de Citas
    # id_cita es la CLAVE PRIMARIA
    # id_mascota es la CLAVE FORÁNEA
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS citas (
            id_cita TEXT PRIMARY KEY,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            motivo TEXT,
            veterinario TEXT,
            id_mascota TEXT,
            FOREIGN KEY (id_mascota) REFERENCES mascotas (id_mascota)
                ON DELETE CASCADE
        )
    """)
    
    # NOTA: Si quieres guardar el Historial Médico, necesitarías otra tabla aquí.
    
    conn.commit()
    conn.close()
    
    return f"Conexión a '{DB_NAME}' establecida y tablas aseguradas."

def get_connection():
    """Devuelve una nueva conexión a la base de datos para usar en CRUD."""
    return sqlite3.connect(DB_NAME)

# Llamada inicial para configurar la BBDD
if __name__ == '__main__':
    print(setup_database())