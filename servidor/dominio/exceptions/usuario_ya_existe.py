class UsuarioYaExiste(Exception):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"El email {email} ya está registrado")
