class UsuarioYaExiste(Exception):
    def __init__(self, email: str, mensaje: str | None = None):
        self.email = email
        super().__init__(mensaje or "Este correo ya está registrado")
