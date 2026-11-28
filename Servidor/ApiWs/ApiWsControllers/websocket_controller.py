from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from Servidor.ApiRest.ApiRestDependencies.auth_dependencies import obtener_email_websocket
from Servidor.ApiWs.gestor_conexiones import gestor

router = APIRouter()


@router.websocket("/ws")
async def endpoint_ws(
    conexion: WebSocket,
    email: str | None = Depends(obtener_email_websocket),
):
    await gestor.conectar(conexion, email)
    try:
        while True:
            mensaje = await conexion.receive_json()
            await gestor.difundir(mensaje)
    except WebSocketDisconnect:
        gestor.desconectar(conexion)
