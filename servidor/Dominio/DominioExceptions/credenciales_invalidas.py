class CredencialesInvalidas(Exception):
    def __init__(self):
        super().__init__("Email o contraseña incorrectos")
