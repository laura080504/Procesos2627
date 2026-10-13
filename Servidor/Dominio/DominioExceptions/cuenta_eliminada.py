class CuentaEliminada(Exception):
    def __init__(self, email: str, mensaje: str = "Usuario eliminado, no puedes iniciar sesión"):
        self.email = email
        super().__init__(mensaje)
