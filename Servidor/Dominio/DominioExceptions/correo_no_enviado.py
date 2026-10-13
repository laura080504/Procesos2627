class CorreoNoEnviado(Exception):
    def __init__(self, mensaje: str = "No se ha podido enviar el correo de confirmación"):
        super().__init__(mensaje)
