from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from servidor.infraestructura.registro_actividad import registro_actividad
from servidor.dominio.exceptions.credenciales_invalidas import CredencialesInvalidas
from servidor.dominio.exceptions.cuenta_pendiente import CuentaPendiente
from servidor.dominio.exceptions.recuperacion_no_valida import RecuperacionNoValida
from servidor.dominio.exceptions.sesion_no_valida import SesionNoValida


async def credenciales_invalidas_handler(_: Request, error: CredencialesInvalidas) -> JSONResponse:
    registro_actividad.fallo(type(error).__name__)
    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": str(error)})


async def cuenta_pendiente_handler(_: Request, error: CuentaPendiente) -> JSONResponse:
    registro_actividad.fallo(type(error).__name__)
    return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": str(error)})


async def sesion_no_valida_handler(_: Request, error: SesionNoValida) -> JSONResponse:
    registro_actividad.fallo(type(error).__name__)
    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": str(error)})


async def recuperacion_no_valida_handler(_: Request, error: RecuperacionNoValida) -> JSONResponse:
    registro_actividad.fallo(type(error).__name__)
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(error)})


def registrar_auth_handlers(aplicacion: FastAPI) -> None:
    aplicacion.add_exception_handler(CredencialesInvalidas, credenciales_invalidas_handler)
    aplicacion.add_exception_handler(CuentaPendiente, cuenta_pendiente_handler)
    aplicacion.add_exception_handler(SesionNoValida, sesion_no_valida_handler)
    aplicacion.add_exception_handler(RecuperacionNoValida, recuperacion_no_valida_handler)
