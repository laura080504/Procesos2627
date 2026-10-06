from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from Servidor.Infraestructura.registro_actividad import registro_actividad
from Servidor.Dominio.DominioExceptions.permiso_insuficiente import PermisoInsuficiente
from Servidor.Dominio.DominioExceptions.usuario_no_encontrado import UsuarioNoEncontrado
from Servidor.Dominio.DominioExceptions.usuario_ya_existe import UsuarioYaExiste


async def usuario_ya_existe_handler(_: Request, error: UsuarioYaExiste) -> JSONResponse:
    registro_actividad.fallo(type(error).__name__)
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": str(error)})


async def usuario_no_encontrado_handler(_: Request, error: UsuarioNoEncontrado) -> JSONResponse:
    registro_actividad.fallo(type(error).__name__)
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(error)})


async def permiso_insuficiente_handler(_: Request, error: PermisoInsuficiente) -> JSONResponse:
    registro_actividad.fallo(type(error).__name__)
    return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": str(error)})


def registrar_usuario_handlers(aplicacion: FastAPI) -> None:
    aplicacion.add_exception_handler(UsuarioYaExiste, usuario_ya_existe_handler)
    aplicacion.add_exception_handler(UsuarioNoEncontrado, usuario_no_encontrado_handler)
    aplicacion.add_exception_handler(PermisoInsuficiente, permiso_insuficiente_handler)
