from fastapi import Depends

from Servidor.ApiRest.ApiRestDependencies.configuracion_dependencies import obtener_hasher_contrasenas
from Servidor.ApiRest.ApiRestDependencies.repositorio_dependencies import (
    obtener_repositorio_recuperaciones,
    obtener_repositorio_sesiones,
    obtener_repositorio_usuarios,
)
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_recuperaciones import RepositorioRecuperaciones
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_sesiones import RepositorioSesiones
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios
from Servidor.Dominio.DominioServices.hasher_contrasenas import HasherContrasenas
from Servidor.Dominio.DominioUseCases.asignar_administrador_use_case import AsignarAdministradorUseCase
from Servidor.Dominio.DominioUseCases.editar_datos_use_case import EditarDatosUseCase
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


def crear_editar_datos_use_case(
    repositorio_usuarios: RepositorioUsuarios = Depends(obtener_repositorio_usuarios),
    repositorio_sesiones: RepositorioSesiones = Depends(obtener_repositorio_sesiones),
    repositorio_recuperaciones: RepositorioRecuperaciones = Depends(obtener_repositorio_recuperaciones),
    hasher: HasherContrasenas = Depends(obtener_hasher_contrasenas),
) -> EditarDatosUseCase:
    return EditarDatosUseCase(
        repositorio_usuarios, repositorio_sesiones, repositorio_recuperaciones, hasher
    )


def crear_asignar_administrador_use_case(
    repositorio_usuarios: RepositorioUsuarios = Depends(obtener_repositorio_usuarios),
) -> AsignarAdministradorUseCase:
    return AsignarAdministradorUseCase(repositorio_usuarios)


def crear_eliminar_usuario_use_case(
    repositorio_usuarios: RepositorioUsuarios = Depends(obtener_repositorio_usuarios),
    repositorio_sesiones: RepositorioSesiones = Depends(obtener_repositorio_sesiones),
    repositorio_recuperaciones: RepositorioRecuperaciones = Depends(obtener_repositorio_recuperaciones),
) -> EliminarUsuarioUseCase:
    return EliminarUsuarioUseCase(repositorio_usuarios, repositorio_sesiones, repositorio_recuperaciones)
