
import sqlite3

DB_NAME = "clinica_vet.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    return conn

def create_tables():
    conn = get_connection()
    c = conn.cursor()
    
    # Tabla Pacientes
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

    # Tabla Citas 
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

    # Tabla Historial 
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

#Nos sirve para cuando queramos hacer cambios en la bbdd, sin esto tendriamos que llamar a la bbdd todo el rato cada vez que queramos cambiar algo
def run_query(query, params=()): 
    conn = get_connection()
    c = conn.cursor()
    c.execute(query, params)
    conn.commit()
    conn.close()

#Nos sirve para cuando queremos mirar y sacar informacion de la bbdd
def read_query(query, params=()):
    conn = get_connection()
    c = conn.cursor()
    c.execute(query, params)
    data = c.fetchall()
    conn.close()
    return data