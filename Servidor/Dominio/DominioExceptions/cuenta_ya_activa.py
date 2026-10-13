class CuentaYaActiva(Exception):
    def __init__(self):
        super().__init__("Esta cuenta ya está confirmada. Puedes iniciar sesión")
