from fastapi import Depends

from Servidor.ApiRest.ApiRestDependencies.repositorio_dependencies import (
    obtener_repositorio_sesiones,
    obtener_repositorio_usuarios,
)
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_sesiones import RepositorioSesiones
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios
from Servidor.Dominio.DominioUseCases.eliminar_usuario_use_case import EliminarUsuarioUseCase
from Servidor.Dominio.DominioUseCases.numero_usuarios_use_case import NumeroUsuariosUseCase
from Servidor.Dominio.DominioUseCases.obtener_usuarios_use_case import ObtenerUsuariosUseCase
from Servidor.Dominio.DominioUseCases.usuario_activo_use_case import UsuarioActivoUseCase


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
