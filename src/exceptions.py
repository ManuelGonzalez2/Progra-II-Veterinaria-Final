class ClienteNoEncontradoError(Exception):
    #Excepción lanzada cuando se intenta operar con un cliente que no existe.
    def __init__(self, id_cliente):
        self.id_cliente = id_cliente
        super().__init__(f"Error: El cliente con ID '{id_cliente}' no se ha encontrado.")

class CitaError(Exception):
    #Excepción base para errores relacionados con la gestión de citas.#
    pass
