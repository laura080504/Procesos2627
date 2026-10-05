from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from servidor.logica.exceptions.credenciales_invalidas import CredencialesInvalidas
from servidor.logica.exceptions.cuenta_pendiente import CuentaPendiente
from servidor.logica.exceptions.sesion_no_valida import SesionNoValida


async def credenciales_invalidas_handler(_: Request, error: CredencialesInvalidas) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": str(error)})


async def cuenta_pendiente_handler(_: Request, error: CuentaPendiente) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": str(error)})


async def sesion_no_valida_handler(_: Request, error: SesionNoValida) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": str(error)})


def registrar_auth_handlers(aplicacion: FastAPI) -> None:
    aplicacion.add_exception_handler(CredencialesInvalidas, credenciales_invalidas_handler)
    aplicacion.add_exception_handler(CuentaPendiente, cuenta_pendiente_handler)
    aplicacion.add_exception_handler(SesionNoValida, sesion_no_valida_handler)
