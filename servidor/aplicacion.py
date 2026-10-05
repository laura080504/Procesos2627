from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from servidor.api_rest.controllers.auth_controller import router as auth_router
from servidor.api_rest.controllers.usuario_controller import router as usuario_router
from servidor.api_rest.handlers.auth_handler import registrar_auth_handlers
from servidor.api_rest.handlers.usuario_handler import registrar_usuario_handlers
from servidor.api_ws.controllers.websocket_controller import router as websocket_router

RUTA_CLIENTE = Path(__file__).resolve().parent.parent / "cliente"

aplicacion = FastAPI(title="Procesos 26-27")

aplicacion.include_router(auth_router)
aplicacion.include_router(usuario_router)
aplicacion.include_router(websocket_router)

registrar_auth_handlers(aplicacion)
registrar_usuario_handlers(aplicacion)

# Debe ir al final para no tapar las rutas de la API
aplicacion.mount("/", StaticFiles(directory=RUTA_CLIENTE, html=True), name="cliente")
