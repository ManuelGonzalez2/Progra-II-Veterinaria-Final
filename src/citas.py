from datetime import date
from .mascotas import Mascota
from .clientes import Cliente 

class Cita:
    """
    Representa una cita médica programada en la clínica.
    """
    def __init__(self, fecha: date, hora: str, motivo: str, veterinario: str, mascota: Mascota):
        self.fecha = fecha
        self.hora = hora
        self.motivo = motivo
        self.veterinario = veterinario
        self.mascota = mascota
        
        # El ID de la mascota es crucial para la BBDD
        self.id_mascota = mascota.id 
        
        # Genera un ID único basado en fecha, hora y el ID de la mascota
        self.id_cita = f"{fecha}_{hora}_{self.id_mascota}"