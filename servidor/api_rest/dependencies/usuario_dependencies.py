from fastapi import Depends

from servidor.api_rest.dependencies.repositorio_dependencies import (
    obtener_repositorio_sesiones,
    obtener_repositorio_usuarios,
)
from servidor.datos.repositories.repositorio_sesiones import RepositorioSesiones
from servidor.datos.repositories.repositorio_usuarios import RepositorioUsuarios
from servidor.logica.use_cases.eliminar_usuario_use_case import EliminarUsuarioUseCase
from servidor.logica.use_cases.numero_usuarios_use_case import NumeroUsuariosUseCase
from servidor.logica.use_cases.obtener_usuarios_use_case import ObtenerUsuariosUseCase
from servidor.logica.use_cases.usuario_activo_use_case import UsuarioActivoUseCase


def crear_obtener_usuarios_use_case(
    repositorio_usuarios: RepositorioUsuarios = Depends(obtener_repositorio_usuarios),
) -> ObtenerUsuariosUseCase:
    return ObtenerUsuariosUseCase(repositorio_usuarios)


def crear_usuario_activo_use_case(
    repositorio_usuarios: RepositorioUsuarios = Depends(obtener_repositorio_usuarios),
) -> UsuarioActivoUseCase:
    return UsuarioActivoUseCase(repositorio_usuarios)


def crear_numero_usuarios_use_case(
    repositorio_usuarios: RepositorioUsuarios = Depends(obtener_repositorio_usuarios),
) -> NumeroUsuariosUseCase:
    return NumeroUsuariosUseCase(repositorio_usuarios)


def crear_eliminar_usuario_use_case(
    repositorio_usuarios: RepositorioUsuarios = Depends(obtener_repositorio_usuarios),
    repositorio_sesiones: RepositorioSesiones = Depends(obtener_repositorio_sesiones),
) -> EliminarUsuarioUseCase:
    return EliminarUsuarioUseCase(repositorio_usuarios, repositorio_sesiones)
