from datetime import date
# Nota: Si Mascota da problemas de importación circular, usa un string o import local.
# Pero por ahora lo dejamos así si no falla.
from .db_connection import get_connection

class Cita:
    """
    Representa una cita médica programada en la clínica.
    """
    def __init__(self, fecha: date, hora: str, motivo: str, veterinario: str, mascota):
        self.fecha = fecha
        self.hora = hora
        self.motivo = motivo
        self.veterinario = veterinario
        self.mascota = mascota
        
        # El ID de la mascota es crucial para la BBDD
        self.id_mascota = mascota.id 
        
        # Genera un ID único basado en fecha, hora y el ID de la mascota
        self.id_cita = f"{fecha}_{hora}_{self.id_mascota}"

# --- FUNCIÓN DE BBDD (FUERA DE LA CLASE, SIN TABULACIÓN A LA IZQUIERDA) ---

def registrar_cita_db(nueva_cita):
    """Inserta una nueva cita en la tabla 'citas' de SQLite."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO citas (id_cita, fecha, hora, motivo, veterinario, id_mascota)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            nueva_cita.id_cita, 
            str(nueva_cita.fecha),
            nueva_cita.hora, 
            nueva_cita.motivo, 
            nueva_cita.veterinario, 
            nueva_cita.id_mascota
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error al registrar cita en DB: {e}")
        return False
    finally:
        conn.close()