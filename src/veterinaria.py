import sqlite3
from datetime import datetime, date
from .db_connection import get_connection, setup_database
from .clientes import Cliente, cargar_clientes_db
from .mascotas import Mascota
# OJO: Solo importamos la Clase Cita arriba. La función la importamos abajo.
from .citas import Cita 

class Veterinaria:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Veterinaria, cls).__new__(cls)
            cls._instance.inicializar()
        return cls._instance

    def inicializar(self):
        """Configura la BBDD y carga los datos en memoria."""
        setup_database() # Crea tablas si no existen
        self.clientes = cargar_clientes_db() # Carga clientes y sus mascotas
        self.citas = self.cargar_citas_db()  # Carga las citas
        print("Sistema inicializado con SQLite.")

    def cargar_citas_db(self):
        """Lee las citas de SQLite y reconstruye los objetos en memoria."""
        citas_memoria = []
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id_cita, fecha, hora, motivo, veterinario, id_mascota FROM citas")
            rows = cursor.fetchall()
            
            for row in rows:
                id_c, fecha_str, hora, motivo, vet, id_mascota = row
                
                # Buscar el objeto mascota real en memoria usando el ID
                mascota_obj = self.buscar_mascota_por_id(id_mascota)
                
                if mascota_obj:
                    # Convertir fecha string a objeto date
                    fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                    
                    cita = Cita(fecha_obj, hora, motivo, vet, mascota_obj)
                    cita.id_cita = id_c # Mantener el ID original
                    citas_memoria.append(cita)
        except Exception as e:
            print(f"Error cargando citas: {e}")
        finally:
            conn.close()
        return citas_memoria

    def buscar_mascota_por_id(self, id_mascota):
        """Ayuda a reconectar citas con mascotas."""
        for cliente in self.clientes:
            for mascota in cliente.mascotas:
                if mascota.id == id_mascota:
                    return mascota
        return None

    # ... (Resto de métodos de registrar cliente/mascota siguen igual) ...
    # Aquí pongo solo los métodos clave. Si necesitas el código COMPLETO con todo, dímelo.
    
    def registrar_cliente(self, nombre, telefono, email):
        # ... (Tu código de registrar cliente) ...
        # Asegúrate de usar la versión que te di antes
        nuevo_cliente = Cliente(nombre, telefono, email)
        from .clientes import registrar_cliente_db
        if registrar_cliente_db(nuevo_cliente):
            self.clientes.append(nuevo_cliente)
            return nuevo_cliente
        return None

    def registrar_mascota(self, email_cliente, nombre, especie, raza, fecha_nacimiento):
        cliente = self.buscar_cliente(email_cliente)
        if cliente:
            nueva_mascota = Mascota(nombre, especie, raza, fecha_nacimiento, cliente.id)
            from .mascotas import registrar_mascota_db
            if registrar_mascota_db(nueva_mascota):
                cliente.mascotas.append(nueva_mascota)
                return nueva_mascota
        return None

    def buscar_cliente(self, email):
        for c in self.clientes:
            if c.email.lower() == email.lower():
                return c
        return None

    def crear_cita(self, fecha, hora, motivo, veterinario, mascota):
        """Crea cita y la guarda usando importación local para evitar errores."""
        nueva_cita = Cita(fecha, hora, motivo, veterinario, mascota)
        self.citas.append(nueva_cita)
        
        # --- SOLUCIÓN AL ERROR: Importación LOCAL ---
        from .citas import registrar_cita_db 
        
        if registrar_cita_db(nueva_cita):
            print(f"Cita guardada: {nueva_cita.id_cita}")
        else:
            print("Error guardando cita en BD.")
        return nueva_cita

    def eliminar_cliente(self, email):
        cliente = self.buscar_cliente(email)
        if cliente:
            from .clientes import eliminar_cliente_db
            if eliminar_cliente_db(cliente.id):
                self.clientes.remove(cliente)
                # Recargar citas para limpiar las borradas por cascada
                self.citas = self.cargar_citas_db() 
                return True
        return False
        
    # Agrega aquí tus métodos de anadir_vacuna, peso, etc. si los tienes