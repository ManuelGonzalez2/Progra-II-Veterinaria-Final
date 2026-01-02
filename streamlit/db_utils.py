# db_utils.py (Versión Mejorada 2.0)
import sqlite3

DB_NAME = "clinica_vet.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    return conn

def create_tables():
    conn = get_connection()
    c = conn.cursor()
    
    # Tabla Pacientes (Ahora con datos de contacto y nacimiento)
    c.execute('''
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            especie TEXT,
            raza TEXT,
            fecha_nacimiento TEXT,
            propietario TEXT,
            telefono TEXT,
            email TEXT
        )
    ''')

    # Tabla Citas (Igual que antes + veterinario)
    c.execute('''
        CREATE TABLE IF NOT EXISTS citas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER,
            fecha TEXT,
            hora TEXT,
            motivo TEXT,
            veterinario TEXT,
            FOREIGN KEY(paciente_id) REFERENCES pacientes(id)
        )
    ''')

    # Tabla Historial (Igual que antes)
    c.execute('''
        CREATE TABLE IF NOT EXISTS historial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER,
            fecha TEXT,
            descripcion TEXT,
            tratamiento TEXT,
            FOREIGN KEY(paciente_id) REFERENCES pacientes(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def run_query(query, params=()):
    conn = get_connection()
    c = conn.cursor()
    c.execute(query, params)
    conn.commit()
    conn.close()

def read_query(query, params=()):
    conn = get_connection()
    c = conn.cursor()
    c.execute(query, params)
    data = c.fetchall()
    conn.close()
    return data