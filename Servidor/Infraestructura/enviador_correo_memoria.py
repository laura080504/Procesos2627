from Servidor.Infraestructura.enviador_correo import EnviadorCorreo


class EnviadorCorreoMemoria(EnviadorCorreo):
    def __init__(self):
        self.mensajes: list[tuple[str, str, str]] = []

    def enviar(self, destino: str, asunto: str, cuerpo: str) -> None:
        self.mensajes.append((destino, asunto, cuerpo))
