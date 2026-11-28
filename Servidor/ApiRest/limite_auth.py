"""Límite sencillo de intentos por IP en rutas de autenticación."""

from __future__ import annotations

import os
import time
from collections import defaultdict, deque

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

_VENTANA_SEGUNDOS = 15 * 60
_RUTAS = {
    "/api/auth/inicio-sesion",
    "/api/auth/registro",
    "/api/auth/recuperacion",
    "/api/auth/nueva-contrasena",
    "/api/auth/reenviar-confirmacion",
    "/api/auth/google",
    "/api/auth/uclm",
}


class LimiteAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._intentos: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        max_intentos = int(os.getenv("AUTH_LIMITE_INTENTOS", "20"))
        if max_intentos > 0 and request.url.path in _RUTAS:
            clave = f"{_ip(request)}|{request.url.path}"
            ahora = time.monotonic()
            cola = self._intentos[clave]
            while cola and ahora - cola[0] > _VENTANA_SEGUNDOS:
                cola.popleft()
            if len(cola) >= max_intentos:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"detail": "Demasiados intentos. Espera unos minutos."},
                )
            cola.append(ahora)
        return await call_next(request)


def _ip(request: Request) -> str:
    # El cliente puede anteponer valores. El proxy (Cloud Run) añade la IP real al final.
    reenviada = request.headers.get("x-forwarded-for", "")
    partes = [parte.strip() for parte in reenviada.split(",") if parte.strip()]
    if partes:
        return partes[-1]
    if request.client and request.client.host:
        return request.client.host
    return "desconocida"
