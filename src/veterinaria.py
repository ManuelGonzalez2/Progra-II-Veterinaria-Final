# src/veterinaria.py
from datetime import datetime, date
import pandas as pd
import os

from .clientes import Cliente
from .mascotas import Mascota
from .citas import Cita

class Veterinaria:
    def __init__(self):
        self.clientes = []
        self.citas = []
        self.archivo_db = 'bbdd_veterinaria.csv' 
        self.cargar_datos_iniciales()

    def cargar_datos_iniciales(self):
        """Carga clientes y mascotas desde el CSV al iniciar."""
        if os.path.exists(self.archivo_db):
            try:
                df = pd.read_csv(self.archivo_db, sep=';', encoding='utf-8')
                
                for _, row in df.iterrows():
                    email_cliente = str(row['cliente_email'])
                    cliente_existente = self.buscar_cliente(email_cliente)
                    
                    if not cliente_existente:
                        cliente_existente = Cliente(
                            str(row['cliente_nombre']), 
                            str(row['cliente_telefono']), 
                            email_cliente
                        )
                        self.clientes.append(cliente_existente)
                    
                    try:
                        fecha_nac = datetime.strptime(str(row['mascota_nacimiento']), '%Y-%m-%d').date()
                    except:
                        fecha_nac = datetime.today().date()

                    nueva_mascota = Mascota(
                        str(row['mascota_nombre']),
                        str(row['mascota_especie']),
                        str(row['mascota_raza']),
                        fecha_nac,
                        cliente_existente
                    )
                    
                    cliente_existente.mascotas.append(nueva_mascota)
                
                print(f"✅ Datos cargados: {len(self.clientes)} clientes.")
            except Exception as e:
                print(f"⚠️ Error al cargar datos iniciales: {e}")

    # --- Persistencia (Cliente/Mascota) ---
    def guardar_en_csv(self, cliente, mascota):
        """Añade la nueva línea de Cliente/Mascota al archivo CSV."""
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
        es_primera_vez = not os.path.exists(self.archivo_db)
        df_nuevo.to_csv(self.archivo_db, mode='a', sep=';', index=False, encoding='utf-8', header=es_primera_vez)

    # --- Funciones CRUD ---
    def registrar_cliente(self, nombre, telefono, email):
        if self.buscar_cliente(email): return self.buscar_cliente(email)
        c = Cliente(nombre, telefono, email)
        self.clientes.append(c)
        return c

    def buscar_cliente(self, email):
        for c in self.clientes:
            if c.email == email: return c
        return None
    
    def eliminar_cliente(self, email):
        """
        Elimina un cliente y todas sus mascotas del sistema (memoria y CSV).
        Implementa la operación DELETE del CRUD.
        """
        cliente_a_eliminar = self.buscar_cliente(email)
        
        if cliente_a_eliminar:
            # 1. Eliminar de la lista en memoria
            self.clientes.remove(cliente_a_eliminar)
            
            # 2. Eliminar del archivo CSV reescribiendo el archivo
            if os.path.exists(self.archivo_db):
                df = pd.read_csv(self.archivo_db, sep=';', encoding='utf-8')
                # Filtra todas las filas donde el email_cliente sea igual al email a eliminar
                df_actualizado = df[df['cliente_email'] != email]
                
                # Reescribe el CSV completamente con los clientes restantes
                df_actualizado.to_csv(self.archivo_db, mode='w', sep=';', index=False, encoding='utf-8')
            
            return True # Cliente eliminado
        return False # Cliente no encontrado

    def _actualizar_csv_despues_eliminacion(self):
        """Función auxiliar para reescribir el CSV con los clientes actuales."""
        # Crea un nuevo DataFrame con los clientes y sus mascotas que QUEDAN
        data_to_save = []
        for cliente in self.clientes:
            for mascota in cliente.mascotas:
                data_to_save.append({
                    "cliente_nombre": cliente.nombre,
                    "cliente_email": cliente.email,
                    "cliente_telefono": cliente.telefono,
                    "mascota_nombre": mascota.nombre,
                    "mascota_especie": mascota.especie,
                    "mascota_raza": mascota.raza,
                    "mascota_nacimiento": mascota.fecha_nacimiento
                })
        
        df = pd.DataFrame(data_to_save)
        # Sobreescribe el archivo (mode='w' en lugar de 'a')
        df.to_csv(self.archivo_db, mode='w', sep=';', index=False, encoding='utf-8')
        
    def registrar_mascota(self, email_cliente, nombre_mascota, especie, raza, fecha_nacimiento):
        cliente = self.buscar_cliente(email_cliente)
        if cliente:
            mascota_nueva = Mascota(nombre_mascota, especie, raza, fecha_nacimiento, cliente)
            cliente.mascotas.append(mascota_nueva)
            self.guardar_en_csv(cliente, mascota_nueva)
            return mascota_nueva
        return None

    # --- Citas ---
    def crear_cita(self, fecha, hora, motivo, veterinario, mascota):
        nueva_cita = Cita(fecha, hora, motivo, veterinario, mascota)
        self.citas.append(nueva_cita)
        return nueva_cita
    
    # --- Historial Médico (Funciones Faltantes) ---
    def anadir_vacuna(self, mascota: Mascota, nombre_vacuna: str, fecha: date):
        registro = f"Vacuna: {nombre_vacuna} | Fecha: {fecha.strftime('%d/%m/%Y')}"
        mascota.historial_medico["vacunas"].append(registro)
        print(f"DEBUG: Vacuna '{nombre_vacuna}' registrada para {mascota.nombre}.")

    def anadir_peso(self, mascota: Mascota, peso_kg: float, fecha: date):
        registro = {"fecha": fecha.strftime('%d/%m/%Y'), "peso": peso_kg}
        mascota.historial_medico["peso"].append(registro)
        print(f"DEBUG: Peso '{peso_kg}' registrado para {mascota.nombre}.")

    def anadir_observacion(self, mascota: Mascota, observacion: str, fecha: date):
        registro = f"[{fecha.strftime('%d/%m/%Y')}] OBS: {observacion}"
        mascota.historial_medico["observaciones"].append(registro)
        print(f"DEBUG: Observación registrada para {mascota.nombre}.")

    def anadir_tratamiento(self, mascota: Mascota, tratamiento: str, fecha_inicio: date):
        registro = f"[{fecha_inicio.strftime('%d/%m/%Y')}] TRAT: {tratamiento}"
        mascota.historial_medico["tratamientos"].append(registro)
        print(f"DEBUG: Tratamiento registrado para {mascota.nombre}.")