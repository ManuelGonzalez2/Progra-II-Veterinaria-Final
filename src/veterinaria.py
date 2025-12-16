# src/veterinaria.py

# --- Nuevas Importaciones ---
from datetime import datetime, date
import os
import sqlite3 # Para manejo de errores de BBDD

# Importamos las funciones de persistencia y la clase Cliente/Mascota
from .db_connection import setup_database, get_connection
from .clientes import Cliente, insertar_cliente, eliminar_cliente_db # Necesitamos crear 'eliminar_cliente_db' en clientes.py
from .mascotas import Mascota, insertar_mascota
from .citas import Cita, registrar_cita_db # Necesitamos crear 'registrar_cita_db' en citas.py

class Veterinaria:
    
    # ------------------ INICIALIZACIÓN -------------------
    def __init__(self):
        # 1. Inicializamos la base de datos (crea el archivo .db y las tablas si no existen)
        setup_database() 
        
        # Estructuras de datos en memoria
        self.clientes = []  # Lista de objetos Cliente
        self.citas = []     # Lista de objetos Cita (solo se guarda en memoria)
        
        # 2. Cargamos los datos desde SQLite a la memoria
        self.cargar_datos_iniciales()

    def cargar_datos_iniciales(self):
        """Carga clientes y mascotas desde SQLite al iniciar."""
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # 1. Cargar Clientes
            cursor.execute("SELECT id_cliente, nombre, telefono, email FROM clientes")
            clientes_db = cursor.fetchall() # Obtiene todas las filas de clientes

            for row in clientes_db:
                id_cliente, nombre, telefono, email = row
                
                # Usamos el constructor de Cliente con el ID de la BBDD
                cliente = Cliente(nombre, telefono, email, id_cliente=id_cliente)
                self.clientes.append(cliente)

                # 2. Cargar Mascotas de este Cliente
                cursor.execute("""
                    SELECT id_mascota, nombre, especie, raza, fecha_nacimiento 
                    FROM mascotas 
                    WHERE cliente_id = ?
                """, (id_cliente,))
                mascotas_db = cursor.fetchall()
                
                for m_row in mascotas_db:
                    id_mascota, m_nombre, especie, raza, fecha_nac_str = m_row
                    
                    try:
                        # Convertir la fecha de string a objeto date
                        fecha_nac = datetime.strptime(fecha_nac_str, '%Y-%m-%d').date()
                    except:
                        fecha_nac = datetime.today().date()
                    
                    # Usamos el constructor de Mascota con sus IDs
                    mascota = Mascota(
                        m_nombre, especie, raza, fecha_nac, 
                        cliente_id=id_cliente, 
                        id_mascota=id_mascota
                    )
                    # Relacionamos el objeto Mascota con su objeto Cliente en memoria
                    cliente.mascotas.append(mascota)
            
            # NOTA: Cargar Citas: Se cargan aquí con lógica similar
            
            print(f"✅ Datos cargados desde SQLite: {len(self.clientes)} clientes y sus mascotas.")
        except Exception as e:
            print(f"⚠️ Error al cargar datos iniciales desde SQLite: {e}")
        finally:
            conn.close()

    # --- Funciones CRUD ---
    
    # Se elimina 'guardar_en_csv' y '_actualizar_csv_despues_eliminacion'

    def registrar_cliente(self, nombre, telefono, email):
        # 1. Buscar en memoria para evitar duplicados rápidos (el DB tiene restricción de email UNIQUE)
        if self.buscar_cliente(email): return self.buscar_cliente(email)
        
        # 2. Crear objeto Cliente (genera el ID único)
        c = Cliente(nombre, telefono, email)
        
        # 3. Insertar en BBDD
        if insertar_cliente(c): # Llama a la función de clientes.py
            # 4. Si es exitoso, añadir a la memoria
            self.clientes.append(c)
            return c
        return None # Falló la inserción (ej. email duplicado)


    def buscar_cliente(self, email):
        # Buscamos en la lista de objetos Cliente en memoria
        for c in self.clientes:
            if c.email == email: return c
        return None
    
    
    def eliminar_cliente(self, email):
        """
        Elimina un cliente y todas sus mascotas. Usa DB DELETE CASCADE.
        """
        cliente_a_eliminar = self.buscar_cliente(email)
        
        if cliente_a_eliminar:
            try:
                # 1. Eliminar de SQLite (la tabla mascotas usa ON DELETE CASCADE)
                if eliminar_cliente_db(cliente_a_eliminar.id): # Llama a la función de clientes.py
                    # 2. Si es exitoso, eliminar de la lista en memoria
                    self.clientes.remove(cliente_a_eliminar)
                    return True # Cliente eliminado
                
            except sqlite3.Error as e:
                 print(f"Error en DB al eliminar cliente: {e}")
                 return False

        return False # Cliente no encontrado

    
    def registrar_mascota(self, email_cliente, nombre_mascota, especie, raza, fecha_nacimiento):
        cliente = self.buscar_cliente(email_cliente)
        
        if cliente:
            # 1. Crear el objeto Mascota, usando el ID del cliente como clave foránea
            mascota_nueva = Mascota(
                nombre_mascota, especie, raza, fecha_nacimiento, 
                cliente_id=cliente.id # USAMOS EL ID único del Cliente
            )
            
            # 2. Insertar en BBDD
            if insertar_mascota(mascota_nueva): # Llama a la función de mascotas.py
                # 3. Si es exitoso, añadir a la memoria del objeto Cliente
                cliente.mascotas.append(mascota_nueva)
                return mascota_nueva
        return None

    # --- Citas ---
    def crear_cita(self, fecha, hora, motivo, veterinario, mascota):
        # 1. Crear el objeto Cita
        nueva_cita = Cita(fecha, hora, motivo, veterinario, mascota)
        
        # 2. Registrar en BBDD
        if registrar_cita_db(nueva_cita): # Llama a la función de citas.py
            # 3. Si es exitoso, añadir a la memoria (para acceso rápido)
            self.citas.append(nueva_cita)
            return nueva_cita
        return None
    
    # --- Historial Médico (Funciones Faltantes) ---
    # NOTA: Estas funciones deben actualizar el campo 'historial_medico' de la Mascota en la BBDD.
    # Como el historial es una estructura compleja, por ahora se mantiene en memoria 
    # o se guardaría en una columna de texto/JSON en SQLite.
    
    def anadir_vacuna(self, mascota: Mascota, nombre_vacuna: str, fecha: date):
        registro = f"Vacuna: {nombre_vacuna} | Fecha: {fecha.strftime('%d/%m/%Y')}"
        mascota.historial_medico["vacunas"].append(registro)
        # TODO: AÑADIR LÓGICA DE ACTUALIZACIÓN A SQLITE AQUÍ
        print(f"DEBUG: Vacuna '{nombre_vacuna}' registrada para {mascota.nombre}.")

    # ... (El resto de funciones de historial quedan igual por ahora) ...
