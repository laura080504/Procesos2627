from fastapi import Depends

from servidor.datos.repositories import RepositorioUsuarios, RepositorioUsuariosMemoria
from servidor.logica.use_cases import (
    AgregarUsuarioUseCase,
    EliminarUsuarioUseCase,
    NumeroUsuariosUseCase,
    ObtenerUsuariosUseCase,
    UsuarioActivoUseCase,
)

_repositorio_usuarios = RepositorioUsuariosMemoria()


def obtener_repositorio_usuarios() -> RepositorioUsuarios:
    return _repositorio_usuarios


def crear_agregar_usuario_use_case(
    repositorio: RepositorioUsuarios = Depends(obtener_repositorio_usuarios),
) -> AgregarUsuarioUseCase:
    return AgregarUsuarioUseCase(repositorio)


def crear_obtener_usuarios_use_case(
    repositorio: RepositorioUsuarios = Depends(obtener_repositorio_usuarios),
) -> ObtenerUsuariosUseCase:
    return ObtenerUsuariosUseCase(repositorio)


def crear_usuario_activo_use_case(
    repositorio: RepositorioUsuarios = Depends(obtener_repositorio_usuarios),
) -> UsuarioActivoUseCase:
    return UsuarioActivoUseCase(repositorio)


def crear_numero_usuarios_use_case(
    repositorio: RepositorioUsuarios = Depends(obtener_repositorio_usuarios),
) -> NumeroUsuariosUseCase:
    return NumeroUsuariosUseCase(repositorio)


def crear_eliminar_usuario_use_case(
    repositorio: RepositorioUsuarios = Depends(obtener_repositorio_usuarios),
) -> EliminarUsuarioUseCase:
    return EliminarUsuarioUseCase(repositorio)
