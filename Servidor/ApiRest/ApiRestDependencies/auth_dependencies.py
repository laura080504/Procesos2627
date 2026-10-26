from datetime import timedelta

from fastapi import Depends, Request

from Servidor.ApiRest.ApiRestDependencies.repositorio_dependencies import (
    obtener_enviador_correo,
    obtener_repositorio_confirmaciones,
    obtener_repositorio_recuperaciones,
    obtener_repositorio_sesiones,
    obtener_repositorio_usuarios,
)
from Servidor.ApiRest.ApiRestDependencies.configuracion_dependencies import (
    obtener_configuracion,
    obtener_hasher_contrasenas,
)
from Servidor.configuracion import Configuracion
from Servidor.Infraestructura.cliente_google import ClienteGoogle
from Servidor.Infraestructura.enviador_correo import EnviadorCorreo
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_confirmaciones import RepositorioConfirmaciones
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_recuperaciones import RepositorioRecuperaciones
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_sesiones import RepositorioSesiones
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios
from Servidor.Dominio.DominioEntities.usuario import Usuario
from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Dominio.DominioExceptions.permiso_insuficiente import PermisoInsuficiente
from Servidor.Dominio.DominioExceptions.sesion_no_valida import SesionNoValida
from Servidor.Dominio.DominioQueries.obtener_usuario_sesion_query import ObtenerUsuarioSesionQuery
from Servidor.Dominio.DominioServices.hasher_contrasenas import HasherContrasenas
from Servidor.Dominio.DominioUseCases.cerrar_sesion_use_case import CerrarSesionUseCase
from Servidor.Dominio.DominioUseCases.confirmar_cuenta_use_case import ConfirmarCuentaUseCase
from Servidor.Dominio.DominioUseCases.emitir_confirmacion_use_case import EmitirConfirmacionUseCase
from Servidor.Dominio.DominioUseCases.iniciar_sesion_google_use_case import IniciarSesionGoogleUseCase
from Servidor.Dominio.DominioUseCases.iniciar_sesion_use_case import IniciarSesionUseCase
from Servidor.Dominio.DominioUseCases.obtener_usuario_sesion_use_case import ObtenerUsuarioSesionUseCase
from Servidor.Dominio.DominioUseCases.registrar_usuario_use_case import RegistrarUsuarioUseCase
from Servidor.Dominio.DominioUseCases.restablecer_contrasena_use_case import RestablecerContrasenaUseCase
from Servidor.Dominio.DominioUseCases.solicitar_recuperacion_use_case import SolicitarRecuperacionUseCase


def crear_emitir_confirmacion_use_case(
    repositorio_usuarios: RepositorioUsuarios = Depends(obtener_repositorio_usuarios),
    repositorio_confirmaciones: RepositorioConfirmaciones = Depends(obtener_repositorio_confirmaciones),
    enviador: EnviadorCorreo = Depends(obtener_enviador_correo),
) -> EmitirConfirmacionUseCase:
    return EmitirConfirmacionUseCase(
        repositorio_usuarios, repositorio_confirmaciones, enviador, timedelta(hours=24)
    )


def crear_registrar_usuario_use_case(
    repositorio_usuarios: RepositorioUsuarios = Depends(obtener_repositorio_usuarios),
    hasher: HasherContrasenas = Depends(obtener_hasher_contrasenas),
    emitir_confirmacion: EmitirConfirmacionUseCase = Depends(crear_emitir_confirmacion_use_case),
) -> RegistrarUsuarioUseCase:
    return RegistrarUsuarioUseCase(repositorio_usuarios, hasher, emitir_confirmacion)


def crear_confirmar_cuenta_use_case(
    repositorio_usuarios: RepositorioUsuarios = Depends(obtener_repositorio_usuarios),
    repositorio_confirmaciones: RepositorioConfirmaciones = Depends(obtener_repositorio_confirmaciones),
) -> ConfirmarCuentaUseCase:
    return ConfirmarCuentaUseCase(repositorio_usuarios, repositorio_confirmaciones)


def crear_iniciar_sesion_google_use_case(
    repositorio_usuarios: RepositorioUsuarios = Depends(obtener_repositorio_usuarios),
    repositorio_sesiones: RepositorioSesiones = Depends(obtener_repositorio_sesiones),
    hasher: HasherContrasenas = Depends(obtener_hasher_contrasenas),
    configuracion: Configuracion = Depends(obtener_configuracion),
    repositorio_confirmaciones: RepositorioConfirmaciones = Depends(obtener_repositorio_confirmaciones),
) -> IniciarSesionGoogleUseCase:
    return IniciarSesionGoogleUseCase(
        repositorio_usuarios,
        repositorio_sesiones,
        hasher,
        configuracion.duracion_sesion,
        repositorio_confirmaciones,
    )


_cliente_google = ClienteGoogle()


def obtener_cliente_google() -> ClienteGoogle:
    return _cliente_google


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


def obtener_gestor(usuario: Usuario = Depends(obtener_usuario_actual)) -> Usuario:
    if usuario.rol not in (Rol.PROFESOR, Rol.SUPERADMINISTRADOR):
        raise PermisoInsuficiente()
    return usuario


def obtener_superadministrador(usuario: Usuario = Depends(obtener_usuario_actual)) -> Usuario:
    if usuario.rol != Rol.SUPERADMINISTRADOR:
        raise PermisoInsuficiente()
    return usuario
