class OauthNoValido(Exception):
    def __init__(self):
        super().__init__("No se ha podido entrar con Google")
