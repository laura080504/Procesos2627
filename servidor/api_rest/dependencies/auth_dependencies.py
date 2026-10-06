from datetime import timedelta

from fastapi import Depends, Request

from servidor.api_rest.dependencies.repositorio_dependencies import (
    obtener_repositorio_recuperaciones,
    obtener_repositorio_sesiones,
    obtener_repositorio_usuarios,
)
from servidor.api_rest.dependencies.configuracion_dependencies import (
    obtener_configuracion,
    obtener_hasher_contrasenas,
)
from servidor.configuracion import Configuracion
from servidor.infraestructura.repositories.repositorio_recuperaciones import RepositorioRecuperaciones
from servidor.infraestructura.repositories.repositorio_sesiones import RepositorioSesiones
from servidor.infraestructura.repositories.repositorio_usuarios import RepositorioUsuarios
from servidor.dominio.entities.usuario import Usuario
from servidor.dominio.exceptions.sesion_no_valida import SesionNoValida
from servidor.dominio.queries.obtener_usuario_sesion_query import ObtenerUsuarioSesionQuery
from servidor.dominio.services.hasher_contrasenas import HasherContrasenas
from servidor.dominio.use_cases.cerrar_sesion_use_case import CerrarSesionUseCase
from servidor.dominio.use_cases.iniciar_sesion_use_case import IniciarSesionUseCase
from servidor.dominio.use_cases.obtener_usuario_sesion_use_case import ObtenerUsuarioSesionUseCase
from servidor.dominio.use_cases.registrar_usuario_use_case import RegistrarUsuarioUseCase
from servidor.dominio.use_cases.restablecer_contrasena_use_case import RestablecerContrasenaUseCase
from servidor.dominio.use_cases.solicitar_recuperacion_use_case import SolicitarRecuperacionUseCase


def crear_registrar_usuario_use_case(
    repositorio_usuarios: RepositorioUsuarios = Depends(obtener_repositorio_usuarios),
    hasher: HasherContrasenas = Depends(obtener_hasher_contrasenas),
) -> RegistrarUsuarioUseCase:
    return RegistrarUsuarioUseCase(repositorio_usuarios, hasher)


def crear_iniciar_sesion_use_case(
    repositorio_usuarios: RepositorioUsuarios = Depends(obtener_repositorio_usuarios),
    repositorio_sesiones: RepositorioSesiones = Depends(obtener_repositorio_sesiones),
    hasher: HasherContrasenas = Depends(obtener_hasher_contrasenas),
    configuracion: Configuracion = Depends(obtener_configuracion),
) -> IniciarSesionUseCase:
    return IniciarSesionUseCase(
        repositorio_usuarios, repositorio_sesiones, hasher, configuracion.duracion_sesion
    )


def crear_cerrar_sesion_use_case(
    repositorio_sesiones: RepositorioSesiones = Depends(obtener_repositorio_sesiones),
) -> CerrarSesionUseCase:
    return CerrarSesionUseCase(repositorio_sesiones)


def crear_obtener_usuario_sesion_use_case(
    repositorio_sesiones: RepositorioSesiones = Depends(obtener_repositorio_sesiones),
    repositorio_usuarios: RepositorioUsuarios = Depends(obtener_repositorio_usuarios),
) -> ObtenerUsuarioSesionUseCase:
    return ObtenerUsuarioSesionUseCase(repositorio_sesiones, repositorio_usuarios)


def crear_solicitar_recuperacion_use_case(
    repositorio_usuarios: RepositorioUsuarios = Depends(obtener_repositorio_usuarios),
    repositorio_recuperaciones: RepositorioRecuperaciones = Depends(obtener_repositorio_recuperaciones),
) -> SolicitarRecuperacionUseCase:
    return SolicitarRecuperacionUseCase(
        repositorio_usuarios, repositorio_recuperaciones, timedelta(minutes=15)
    )


def crear_restablecer_contrasena_use_case(
    repositorio_usuarios: RepositorioUsuarios = Depends(obtener_repositorio_usuarios),
    repositorio_recuperaciones: RepositorioRecuperaciones = Depends(obtener_repositorio_recuperaciones),
    repositorio_sesiones: RepositorioSesiones = Depends(obtener_repositorio_sesiones),
    hasher: HasherContrasenas = Depends(obtener_hasher_contrasenas),
) -> RestablecerContrasenaUseCase:
    return RestablecerContrasenaUseCase(
        repositorio_usuarios, repositorio_recuperaciones, repositorio_sesiones, hasher
    )


def obtener_token_sesion(
    request: Request,
    configuracion: Configuracion = Depends(obtener_configuracion),
) -> str | None:
    return request.cookies.get(configuracion.nombre_cookie_sesion)


def obtener_usuario_actual(
    token: str | None = Depends(obtener_token_sesion),
    use_case: ObtenerUsuarioSesionUseCase = Depends(crear_obtener_usuario_sesion_use_case),
) -> Usuario:
    if not token:
        raise SesionNoValida()
    return use_case.ejecutar(ObtenerUsuarioSesionQuery(token=token))
