import bcrypt


class HasherContrasenas:
    def __init__(self, rondas: int = 12):
        self.rondas = rondas

    def hashear(self, contrasena: str) -> str:
        return bcrypt.hashpw(contrasena.encode(), bcrypt.gensalt(self.rondas)).decode()

    def verificar(self, contrasena: str, contrasena_hash: str) -> bool:
        return bcrypt.checkpw(contrasena.encode(), contrasena_hash.encode())
