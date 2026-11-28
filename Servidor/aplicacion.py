from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from Servidor.ApiRest.ApiRestControllers.agenda_controller import router as agenda_router
from Servidor.ApiRest.ApiRestControllers.auth_controller import router as auth_router
from Servidor.ApiRest.ApiRestControllers.prueba_controller import router as prueba_router
from Servidor.ApiRest.ApiRestControllers.usuario_controller import router as usuario_router
from Servidor.ApiRest.ApiRestDependencies.configuracion_dependencies import obtener_configuracion
from Servidor.ApiRest.ApiRestHandlers.auth_handler import registrar_auth_handlers
from Servidor.ApiRest.ApiRestHandlers.usuario_handler import registrar_usuario_handlers
from Servidor.ApiRest.limite_auth import LimiteAuthMiddleware
from Servidor.ApiWs.ApiWsControllers.websocket_controller import router as websocket_router
from Servidor.Infraestructura.registro_actividad import configurar_registro_actividad

_configuracion = obtener_configuracion()
configurar_registro_actividad(_configuracion.nivel_registro)

RUTA_CLIENTE = Path(__file__).resolve().parent.parent / "Cliente"
_DOCS = None if _configuracion.cookie_segura else "/docs"
_POLITICA_SEGURIDAD = (
    "default-src 'self'; "
    "base-uri 'self'; "
    "form-action 'self'; "
    "frame-ancestors 'none'; "
    "object-src 'none'; "
    "script-src 'self'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data:; "
    "connect-src 'self'"
)

aplicacion = FastAPI(
    title="Procesos 26-27",
    docs_url=_DOCS,
    redoc_url=None if _configuracion.cookie_segura else "/redoc",
    openapi_url=None if _configuracion.cookie_segura else "/openapi.json",
)


class CabecerasSeguridadMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        respuesta = await call_next(request)
        respuesta.headers.setdefault("X-Content-Type-Options", "nosniff")
        respuesta.headers.setdefault("X-Frame-Options", "DENY")
        respuesta.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        respuesta.headers.setdefault("Permissions-Policy", "camera=(), microphone=(self), geolocation=()")
        respuesta.headers.setdefault("Content-Security-Policy", _POLITICA_SEGURIDAD)
        if _configuracion.cookie_segura:
            respuesta.headers.setdefault(
                "Strict-Transport-Security",
                "max-age=31536000; includeSubDomains",
            )
        return respuesta


aplicacion.add_middleware(LimiteAuthMiddleware)
aplicacion.add_middleware(CabecerasSeguridadMiddleware)

aplicacion.include_router(auth_router)
aplicacion.include_router(usuario_router)
aplicacion.include_router(agenda_router)
aplicacion.include_router(prueba_router)
aplicacion.include_router(websocket_router)

registrar_auth_handlers(aplicacion)
registrar_usuario_handlers(aplicacion)

# Debe ir al final para no tapar las rutas de la API
aplicacion.mount("/", StaticFiles(directory=RUTA_CLIENTE, html=True), name="cliente")