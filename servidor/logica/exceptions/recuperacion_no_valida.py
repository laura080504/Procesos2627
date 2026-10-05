class RecuperacionNoValida(Exception):
    def __init__(self):
        super().__init__("El enlace de recuperación no es válido o ha caducado")
