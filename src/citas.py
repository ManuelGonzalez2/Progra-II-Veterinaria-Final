from datetime import date 

from .mascotas import Mascota

class Cita:
    def __init__(self, fecha: date, hora: str, motivo: str, veterinario: str, mascota: Mascota):
        self.fecha = fecha
        self.hora = hora
        self.motivo = motivo
        self.veterinario = veterinario
        self.mascota = mascota

    def __str__(self):
        return f"Usted tiene cita el {self.fecha} a las {self.hora} para {self.mascota.nombre}"
