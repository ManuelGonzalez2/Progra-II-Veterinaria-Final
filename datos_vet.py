import pandas as pd
import random

# Datos para generar aleatorios
nombres_personas = ["Ana", "Carlos", "Beatriz", "David", "Elena", "Fernando", "Gloria", "Hector", "Irene", "Javier", "Laura", "Manuel", "Natalia", "Oscar", "Patricia", "Raul", "Sara", "Tomas", "Vanessa", "Zoe"]
apellidos = ["Garcia", "Lopez", "Perez", "Gonzalez", "Sanchez", "Martinez", "Rodriguez", "Fernandez", "Gomez", "Martin"]
dominios = ["gmail.com", "hotmail.com", "yahoo.es", "outlook.com"]

nombres_mascotas = ["Toby", "Luna", "Rocky", "Coco", "Max", "Lola", "Thor", "Nala", "Simba", "Kira", "Zeus", "Mia", "Leo", "Noa", "Bimba", "Bruno"]
especies_razas = {
    "Perro": ["Labrador", "Pastor Alemán", "Bulldog", "Caniche", "Golden Retriever", "Mestizo"],
    "Gato": ["Siames", "Persa", "Común Europeo", "Maine Coon", "Bengala"],
    "Ave": ["Periquito", "Canario", "Loro"],
    "Conejo": ["Enano", "Belier", "Cabeza de León"]
}

data = []

# Generamos 20 clientes con sus mascotas
for i in range(20):
    # Generar Cliente
    nombre = random.choice(nombres_personas) + " " + random.choice(apellidos)
    email = f"{nombre.lower().replace(' ', '.')}{random.randint(1,99)}@{random.choice(dominios)}"
    telefono = f"6{random.randint(10000000, 99999999)}"
    
    # Generar Mascota
    especie = random.choice(list(especies_razas.keys()))
    raza = random.choice(especies_razas[especie])
    nombre_mascota = random.choice(nombres_mascotas)
    
    # Fecha nacimiento aleatoria (entre 2015 y 2024)
    anio = random.randint(2015, 2024)
    mes = random.randint(1, 12)
    dia = random.randint(1, 28)
    fecha_nac = f"{dia}/{mes}/{anio}"

    data.append({
        "cliente_nombre": nombre,
        "cliente_email": email,
        "cliente_telefono": telefono,
        "mascota_nombre": nombre_mascota,
        "mascota_especie": especie,
        "mascota_raza": raza,
        "mascota_nacimiento": fecha_nac
    })

# Crear DataFrame y guardar
df = pd.DataFrame(data)
archivo_salida = 'bbdd_veterinaria.csv'
df.to_csv(archivo_salida, sep=';', index=False, encoding='utf-8')

print(f"✅ Base de datos creada: {archivo_salida}")
print(df.head())