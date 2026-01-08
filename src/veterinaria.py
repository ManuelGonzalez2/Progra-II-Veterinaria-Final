import sqlite3
from datetime import datetime, date
from .db_connection import get_connection, setup_database
from .clientes import Cliente, cargar_clientes_db
from .mascotas import Mascota
from .citas import Cita 

class Veterinaria:
    _instance = None

    def __new__(cls): #Usamos Singleton en la clase Veterinaria para centralizar el estado y asegurar que todas las páginas accedan a la misma lista de datos y conexión a la base de datos.
        if cls._instance is None:
            cls._instance = super(Veterinaria, cls).__new__(cls)
            cls._instance.inicializar()
        return cls._instance

    def inicializar(self):
        #Configura la BBDD y carga los datos en memoria.
        print(" Inicializando sistema...")
        setup_database() # Crea tablas si no existen
        
        # Primero carga los  Clientes y sus Mascotas desde SQLite
        self.clientes = cargar_clientes_db() 
        
        # Cargar Citas desde SQLite 
        self.citas = self.cargar_citas_db()  
        
        print("✅ Sistema inicializado correctamente con SQLite.")


    def cargar_citas_db(self):
        citas_memoria = []
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # Pedimos todas las citas
            cursor.execute("SELECT id_cita, fecha, hora, motivo, veterinario, id_mascota FROM citas")
            rows = cursor.fetchall()
            
            for row in rows:
                id_c, fecha_str, hora, motivo, vet, id_mascota = row
                
                # Buscar el objeto mascota real en memoria usando el ID
                mascota_obj = self.buscar_mascota_por_id(id_mascota)
                
                if mascota_obj:
                    # Convertir fecha string a objeto date de Python
                    try:
                        fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                    except ValueError:
                        fecha_obj = date.today() # Por si la fecha viniera mal
                    
                    # Recreamos el objeto Cita
                    cita = Cita(fecha_obj, hora, motivo, vet, mascota_obj)
                    cita.id_cita = id_c # Le volvemos a poner su ID original
                    citas_memoria.append(cita)
        except Exception as e:
            print(f" Error cargando citas: {e}")
        finally:
            conn.close()
        return citas_memoria

    def crear_cita(self, fecha, hora, motivo, veterinario, mascota):
        #Crea una cita en memoria y la guarda en la BBDD.
        nueva_cita = Cita(fecha, hora, motivo, veterinario, mascota)
        self.citas.append(nueva_cita)
        
        from .citas import registrar_cita_db 
        
        if registrar_cita_db(nueva_cita):
            print(f"📅 Cita guardada en BD: {nueva_cita.id_cita}")
        else:
            print(" Error guardando cita en BD.")
        return nueva_cita


    def buscar_cliente(self, email):
        #Busca un cliente por su email.
        for c in self.clientes:
            if c.email.lower() == email.lower():
                return c
        return None

    def buscar_mascota_por_id(self, id_mascota):
        #Busca una mascota por su ID único entre todos los clientes
        for cliente in self.clientes:
            for mascota in cliente.mascotas:
                if mascota.id == id_mascota:
                    return mascota
        return None

    def buscar_mascota_de_cliente(self, email_cliente, nombre_mascota): #Para los clientes que tienen varias mascotas
        #Busca una mascota por nombre dentro de un cliente específico
        cliente = self.buscar_cliente(email_cliente)
        if cliente:
            for m in cliente.mascotas:
                if m.nombre.lower() == nombre_mascota.lower():
                    return m
        return None


    def registrar_cliente(self, nombre, telefono, email):
        #Crea cliente y lo guarda en SQLite.
        # Verificar si ya existe en memoria para ahorrar consulta
        if self.buscar_cliente(email):
            print(" El cliente ya existe en memoria.")
            return None

        nuevo_cliente = Cliente(nombre, telefono, email)
        
        from .clientes import registrar_cliente_db
        
        if registrar_cliente_db(nuevo_cliente):
            self.clientes.append(nuevo_cliente)
            print(f"👤 Cliente registrado: {nombre}")
            return nuevo_cliente
        return None

    def eliminar_cliente(self, email):
        #Borra cliente de memoria y BBDD y sus mascotas en tambien
        cliente = self.buscar_cliente(email)
        if cliente:
            from .clientes import eliminar_cliente_db
            if eliminar_cliente_db(cliente.id):
                self.clientes.remove(cliente)
                # Recargamos citas para que desaparezcan las de este cliente
                self.citas = self.cargar_citas_db() 
                print(f"🗑️ Cliente {email} eliminado.")
                return True
        return False

    def registrar_mascota(self, email_cliente, nombre, especie, raza, fecha_nacimiento):
        #Añade una mascota a un cliente existente y guarda en SQLite.
        cliente = self.buscar_cliente(email_cliente)
        
        if cliente:
            nueva_mascota = Mascota(nombre, especie, raza, fecha_nacimiento, cliente.id)
            from .mascotas import registrar_mascota_db
            
            if registrar_mascota_db(nueva_mascota):
                cliente.mascotas.append(nueva_mascota)
                print(f"🐾 Mascota {nombre} registrada a {cliente.nombre}.")
                return nueva_mascota
            else:
                print(" Fallo al guardar mascota en BD.")
        else:
            print(" No se encontró al cliente.")
        return None


    def anadir_vacuna(self, email_cliente, nombre_mascota, vacuna, fecha):
        #Registra una vacuna en el historial de la mascota
        mascota = self.buscar_mascota_de_cliente(email_cliente, nombre_mascota)
        
        if mascota:
            registro = {"nombre": vacuna, "fecha": str(fecha)}
            mascota.historial_medico["vacunas"].append(registro)
            print(f"💉 Vacuna '{vacuna}' registrada a {nombre_mascota}.")
            return True
        else:
            print("No se encontró la mascota o el cliente para vacunar.")
            return False

    def registrar_peso(self, email_cliente, nombre_mascota, peso, fecha):
        #Registra el peso en el historial
        mascota = self.buscar_mascota_de_cliente(email_cliente, nombre_mascota)
        
        if mascota:
            registro = {"peso": peso, "fecha": str(fecha)}
            mascota.historial_medico["peso"].append(registro)
            print(f"⚖️ Peso de {peso}kg registrado a {nombre_mascota}.")
            return True
        else:
            print("No se encontró la mascota o el cliente para vacunar.")
            return False

    def anadir_observacion(self, email_cliente, nombre_mascota, texto_observacion):
        #Añade observaciones veterinarias
        mascota = self.buscar_mascota_de_cliente(email_cliente, nombre_mascota)
        
        if mascota:
            mascota.historial_medico["observaciones"].append(texto_observacion)
            print(f"📝 Observación añadida a {nombre_mascota}.")
            return True
        else:
            print("No se encontró la mascota o el cliente para vacunar.")
            return False