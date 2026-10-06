from fastapi import WebSocket


class GestorConexiones:
    def __init__(self):
        self.conexiones: list[WebSocket] = []

    async def conectar(self, conexion: WebSocket):
        await conexion.accept()
        self.conexiones.append(conexion)

    def desconectar(self, conexion: WebSocket):
        self.conexiones.remove(conexion)

    async def difundir(self, mensaje: dict):
        for conexion in self.conexiones:
            await conexion.send_json(mensaje)


gestor = GestorConexiones()
