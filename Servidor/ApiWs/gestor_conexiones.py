from fastapi import WebSocket


class GestorConexiones:
    def __init__(self):
        self.conexiones: dict[WebSocket, str | None] = {}

    async def conectar(self, conexion: WebSocket, email: str | None = None):
        await conexion.accept()
        self.conexiones[conexion] = email

    def desconectar(self, conexion: WebSocket):
        self.conexiones.pop(conexion, None)

    def emails_conectados(self) -> set[str]:
        return {email for email in self.conexiones.values() if email}

    async def difundir(self, mensaje: dict, destinatarios: set[str] | None = None):
        for conexion, email in list(self.conexiones.items()):
            if destinatarios is not None and email not in destinatarios:
                continue
            try:
                await conexion.send_json(mensaje)
            except Exception:
                self.desconectar(conexion)


gestor = GestorConexiones()
