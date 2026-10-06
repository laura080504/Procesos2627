from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from servidor.dominio.exceptions.usuario_no_encontrado import UsuarioNoEncontrado
from servidor.dominio.exceptions.usuario_ya_existe import UsuarioYaExiste


async def usuario_ya_existe_handler(_: Request, error: UsuarioYaExiste) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": str(error)})


async def usuario_no_encontrado_handler(_: Request, error: UsuarioNoEncontrado) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(error)})


def registrar_usuario_handlers(aplicacion: FastAPI) -> None:
    aplicacion.add_exception_handler(UsuarioYaExiste, usuario_ya_existe_handler)
    aplicacion.add_exception_handler(UsuarioNoEncontrado, usuario_no_encontrado_handler)
