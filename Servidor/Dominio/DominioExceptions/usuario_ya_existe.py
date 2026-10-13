class UsuarioYaExiste(Exception):
    def __init__(self, email: str):
        self.email = email
        super().__init__("Este correo ya está registrado")
