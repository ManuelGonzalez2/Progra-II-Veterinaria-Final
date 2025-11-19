from datetime import date 

class Mascota:
    def __init__(self, nombre: str, especie: str, raza: str, fecha_nacimiento: date):
        self.nombre = nombre
        self.especie = especie
        self.raza = raza
        self.fecha_nacimiento = fecha_nacimiento
        # Creamos un historial medico de cad mascota donde se recogeran diferetes atributos
        self.historial_medico = {
            "vacunas": [],
            "peso": [],
            "observaciones": [],
            "tratamientos": []
        }

    def __str__(self):
        return f"Mascota: {self.nombre} (Especie: {self.especie})"
