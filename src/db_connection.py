class DatabaseConnection:
    "Clase para gestionar la conexión a la Base de Datos."
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = None
    
    def connect(self):
        "Intenta establecer la conexión con la BBDD."
        print(f"Conectando a {self.db_file}...")
        pass

    def disconnect(self):
        "Cierra la conexión activa."
        print("Desconectando de la BBDD...")
        if self.conn:
            pass
