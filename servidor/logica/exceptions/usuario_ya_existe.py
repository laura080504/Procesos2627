class UsuarioYaExiste(Exception):
    def __init__(self, nick: str):
        self.nick = nick
        super().__init__(f"El usuario {nick} ya existe")
