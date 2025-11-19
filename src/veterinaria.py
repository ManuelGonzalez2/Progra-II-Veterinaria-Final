# src/veterinaria.py
from datetime import datetime
import pandas as pd
import os

from .clientes import Cliente
from .mascotas import Mascota
from .citas import Cita

class Veterinaria:
    def __init__(self):
        self.clientes = []
        self.citas = []
        self.archivo_db = 'bbdd_veterinaria.csv' # Nombre del archivo
        self.cargar_datos_iniciales()

    def cargar_datos_iniciales(self):
        """Carga clientes y mascotas desde el CSV al iniciar"""
        if os.path.exists(self.archivo_db):
            try:
                df = pd.read_csv(self.archivo_db, sep=';', encoding='utf-8')
                
                for _, row in df.iterrows():
                    # Buscamos si el cliente ya existe en memoria para no duplicarlo
                    email_cliente = str(row['cliente_email'])
                    cliente_existente = self.buscar_cliente(email_cliente)
                    
                    if not cliente_existente:
                        cliente_existente = Cliente(
                            str(row['cliente_nombre']), 
                            str(row['cliente_telefono']), 
                            email_cliente
                        )
                        self.clientes.append(cliente_existente)
                    
                    # Creamos la Mascota
                    try:
                        fecha_nac = datetime.strptime(str(row['mascota_nacimiento']), '%Y-%m-%d').date()
                    except:
                        # Intentamos formato español o ponemos hoy
                        try:
                            fecha_nac = datetime.strptime(str(row['mascota_nacimiento']), '%d/%m/%Y').date()
                        except:
                            fecha_nac = datetime.today().date()

                    nueva_mascota = Mascota(
                        str(row['mascota_nombre']),
                        str(row['mascota_especie']),
                        str(row['mascota_raza']),
                        fecha_nac
                    )
                    
                    cliente_existente.mascotas.append(nueva_mascota)
                
                print(f"✅ Datos cargados correctamente.")
            except Exception as e:
                print(f"⚠️ Error al cargar datos: {e}")

    def guardar_en_csv(self, cliente, mascota):
        """Escribe una nueva línea en el archivo CSV para que no se pierda"""
        nuevo_dato = {
            "cliente_nombre": [cliente.nombre],
            "cliente_email": [cliente.email],
            "cliente_telefono": [cliente.telefono],
            "mascota_nombre": [mascota.nombre],
            "mascota_especie": [mascota.especie],
            "mascota_raza": [mascota.raza],
            "mascota_nacimiento": [mascota.fecha_nacimiento]
        }
        df_nuevo = pd.DataFrame(nuevo_dato)
        
        # Escribimos en el archivo en modo 'append' (añadir al final) sin borrar lo anterior
        # Si el archivo no existe, lo crea con cabeceras. Si existe, no pone cabeceras.
        es_primera_vez = not os.path.exists(self.archivo_db)
        df_nuevo.to_csv(self.archivo_db, mode='a', sep=';', index=False, encoding='utf-8', header=es_primera_vez)

    # --- Funciones de Clientes ---
    def registrar_cliente(self, nombre, telefono, email):
        # Primero miramos si ya existe para no duplicar
        if self.buscar_cliente(email):
            return self.buscar_cliente(email)
            
        c = Cliente(nombre, telefono, email)
        self.clientes.append(c)
        return c

    def buscar_cliente(self, email):
        for c in self.clientes:
            if c.email == email: return c
        return None
        
    # --- Funciones de Mascotas ---
    def registrar_mascota(self, email_cliente, nombre_mascota, especie, raza, fecha_nacimiento):
        cliente = self.buscar_cliente(email_cliente)
        if cliente:
            m = Mascota(nombre_mascota, especie, raza, fecha_nacimiento)
            cliente.mascotas.append(m)
            
            # ¡AQUÍ ESTÁ LA CLAVE! GUARDAMOS EN EL DISCO DURO
            self.guardar_en_csv(cliente, m)
            
            return m
        return None

    # --- Funciones de Citas ---
    def crear_cita(self, fecha, hora, motivo, veterinario, mascota):
        c = Cita(fecha, hora, motivo, veterinario, mascota)
        self.citas.append(c)
        return c