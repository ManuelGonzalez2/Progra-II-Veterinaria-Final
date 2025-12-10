# src/mascotas.py
from datetime import date
from .clientes import Cliente 

class Mascota:
    """
    Representa a una mascota. Ahora guarda una referencia directa al objeto Cliente dueño (self.cliente).
    """
    def __init__(self, nombre: str, especie: str, raza: str, fecha_nacimiento: date, cliente: Cliente): # <-- CLAVE: Acepta el objeto Cliente
        self.nombre = nombre
        self.especie = especie
        self.raza = raza
        self.fecha_nacimiento = fecha_nacimiento
        self.cliente = cliente # <-- Guarda el objeto Cliente completo
        
        self.historial_medico = {
            "vacunas": [],
            "peso": [],
            "observaciones": [],
            "tratamientos": []
        }

    def __str__(self):
        return f"Mascota: {self.nombre} (Dueño: {self.cliente.nombre})"