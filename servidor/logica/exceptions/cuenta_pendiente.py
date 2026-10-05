class CuentaPendiente(Exception):
    def __init__(self, email: str):
        self.email = email
        super().__init__("La cuenta está pendiente de confirmar")
