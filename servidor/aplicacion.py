from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from servidor.api_rest.controllers import usuario_router
from servidor.api_rest.handlers import registrar_usuario_handlers
from servidor.api_ws.controllers import websocket_router

RUTA_CLIENTE = Path(__file__).resolve().parent.parent / "cliente"

aplicacion = FastAPI(title="Procesos 26-27")

aplicacion.include_router(usuario_router)
aplicacion.include_router(websocket_router)
registrar_usuario_handlers(aplicacion)

# Debe ir al final para no tapar las rutas de la API
aplicacion.mount("/", StaticFiles(directory=RUTA_CLIENTE, html=True), name="cliente")
