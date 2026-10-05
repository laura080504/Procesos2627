class UsuarioNoEncontrado(Exception):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"El usuario {email} no existe")
