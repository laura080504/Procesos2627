class SesionNoValida(Exception):
    def __init__(self):
        super().__init__("Sesión no válida o caducada")
