from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from servidor.api_ws.gestor_conexiones import gestor

router = APIRouter()


@router.websocket("/ws")
async def endpoint_ws(conexion: WebSocket):
    await gestor.conectar(conexion)
    try:
        while True:
            mensaje = await conexion.receive_json()
            await gestor.difundir(mensaje)
    except WebSocketDisconnect:
        gestor.desconectar(conexion)
