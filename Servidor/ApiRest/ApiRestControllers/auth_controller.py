from fastapi import APIRouter, Depends, Response, status

from Servidor.ApiRest.ApiRestDependencies.auth_dependencies import (
    crear_cerrar_sesion_use_case,
    crear_iniciar_sesion_use_case,
    crear_registrar_usuario_use_case,
    crear_restablecer_contrasena_use_case,
    crear_solicitar_recuperacion_use_case,
    obtener_token_sesion,
    obtener_usuario_actual,
)
from Servidor.ApiRest.ApiRestDependencies.configuracion_dependencies import obtener_configuracion
from Servidor.ApiRest.ApiRestSchemas.inicio_sesion_entrada import InicioSesionEntrada
from Servidor.ApiRest.ApiRestSchemas.nueva_contrasena_entrada import NuevaContrasenaEntrada
from Servidor.ApiRest.ApiRestSchemas.recuperacion_entrada import RecuperacionEntrada
from Servidor.ApiRest.ApiRestSchemas.recuperacion_salida import RecuperacionSalida
from Servidor.ApiRest.ApiRestSchemas.registro_entrada import RegistroEntrada
from Servidor.ApiRest.ApiRestSchemas.usuario_salida import UsuarioSalida
from Servidor.configuracion import Configuracion
from Servidor.Infraestructura.registro_actividad import registro_actividad
from Servidor.Dominio.DominioCommands.cerrar_sesion_command import CerrarSesionCommand
from Servidor.Dominio.DominioCommands.iniciar_sesion_command import IniciarSesionCommand
from Servidor.Dominio.DominioCommands.registrar_usuario_command import RegistrarUsuarioCommand
from Servidor.Dominio.DominioCommands.restablecer_contrasena_command import RestablecerContrasenaCommand
from Servidor.Dominio.DominioCommands.solicitar_recuperacion_command import SolicitarRecuperacionCommand
from Servidor.Dominio.DominioEntities.usuario import Usuario
from Servidor.Dominio.DominioUseCases.cerrar_sesion_use_case import CerrarSesionUseCase
from Servidor.Dominio.DominioUseCases.iniciar_sesion_use_case import IniciarSesionUseCase
from Servidor.Dominio.DominioUseCases.registrar_usuario_use_case import RegistrarUsuarioUseCase
from Servidor.Dominio.DominioUseCases.restablecer_contrasena_use_case import RestablecerContrasenaUseCase
from Servidor.Dominio.DominioUseCases.solicitar_recuperacion_use_case import SolicitarRecuperacionUseCase

router = APIRouter(prefix="/api/auth", tags=["autenticación"])


@router.post("/registro", response_model=UsuarioSalida, status_code=status.HTTP_201_CREATED)
def registrar(
    datos: RegistroEntrada,
    use_case: RegistrarUsuarioUseCase = Depends(crear_registrar_usuario_use_case),
):
    usuario = use_case.ejecutar(
        RegistrarUsuarioCommand(email=datos.email, nick=datos.nick, contrasena=datos.contrasena)
    )
    registro_actividad.alta(usuario.email)
    return usuario


@router.post("/inicio-sesion", response_model=UsuarioSalida)
def iniciar_sesion(
    datos: InicioSesionEntrada,
    response: Response,
    use_case: IniciarSesionUseCase = Depends(crear_iniciar_sesion_use_case),
    configuracion: Configuracion = Depends(obtener_configuracion),
):
    resultado = use_case.ejecutar(IniciarSesionCommand(email=datos.email, contrasena=datos.contrasena))
    registro_actividad.inicio(resultado.usuario.email)
    response.set_cookie(
        key=configuracion.nombre_cookie_sesion,
        value=resultado.sesion.token,
        max_age=int(configuracion.duracion_sesion.total_seconds()),
        httponly=True,
        secure=configuracion.cookie_segura,
        samesite="lax",
    )
    return resultado.usuario


@router.post("/cierre-sesion", status_code=status.HTTP_204_NO_CONTENT)
def cerrar_sesion(
    response: Response,
    token: str | None = Depends(obtener_token_sesion),
    use_case: CerrarSesionUseCase = Depends(crear_cerrar_sesion_use_case),
    configuracion: Configuracion = Depends(obtener_configuracion),
):
    if token:
        use_case.ejecutar(CerrarSesionCommand(token=token))
        registro_actividad.cierre()
    response.delete_cookie(configuracion.nombre_cookie_sesion)


@router.get("/sesion", response_model=UsuarioSalida)
def obtener_sesion(usuario: Usuario = Depends(obtener_usuario_actual)):
    return usuario


@router.post("/recuperacion", response_model=RecuperacionSalida)
def solicitar_recuperacion(
    datos: RecuperacionEntrada,
    use_case: SolicitarRecuperacionUseCase = Depends(crear_solicitar_recuperacion_use_case),
):
    recuperacion = use_case.ejecutar(SolicitarRecuperacionCommand(email=datos.email))
    return RecuperacionSalida(token=recuperacion.token)


@router.post("/nueva-contrasena", status_code=status.HTTP_204_NO_CONTENT)
def restablecer_contrasena(
    datos: NuevaContrasenaEntrada,
    use_case: RestablecerContrasenaUseCase = Depends(crear_restablecer_contrasena_use_case),
):
    use_case.ejecutar(RestablecerContrasenaCommand(token=datos.token, contrasena=datos.contrasena))
