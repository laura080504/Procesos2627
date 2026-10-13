class ConfirmacionNoValida(Exception):
    def __init__(self):
        super().__init__("El enlace de confirmación no es válido o ha caducado")
