class Utils:
    def validar_email(email):
        #Comprueba si un email tiene un formato básico válido
        if "@" in str(email) and "." in str(email):
            return True
        return False
    
    def formatear_nombre(nombre):
        #Convierte un nombre a formato Título y elimina espacios extr
        return str(nombre).strip().title()
