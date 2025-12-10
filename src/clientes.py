from datetime import date 

class Cliente:
    def __init__(self, nombre: str, telefono: str, email: str):
        self.nombre = nombre
        self.telefono = telefono
        self.email = email
        self.mascotas = [] # Creamos una lista para guardar las masotas de cada cliente

    def __str__(self):
        return f"Cliente: {self.nombre} , con mail ({self.email})"
