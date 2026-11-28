from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from Servidor.ApiRest.ApiRestDependencies.auth_dependencies import obtener_email_websocket
from Servidor.ApiWs.gestor_conexiones import gestor

router = APIRouter()


def _mismo_origen(conexion: WebSocket) -> bool:
    origen = conexion.headers.get("origin")
    if not origen:
        return True
    host = conexion.headers.get("host", "")
    return bool(host) and origen in {f"http://{host}", f"https://{host}"}


@router.websocket("/ws")
async def endpoint_ws(
    conexion: WebSocket,
    email: str | None = Depends(obtener_email_websocket),
):
    if not email or not _mismo_origen(conexion):
        await conexion.close(code=1008)
        return
    await gestor.conectar(conexion, email)
    try:
        while True:
            # El canal solo empuja avisos del servidor. Lo que envíe el cliente se descarta.
            await conexion.receive_text()
    except WebSocketDisconnect:
        gestor.desconectar(conexion)
