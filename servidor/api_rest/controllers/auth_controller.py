from fastapi import APIRouter, Depends, Response, status

from servidor.api_rest.dependencies.auth_dependencies import (
    crear_cerrar_sesion_use_case,
    crear_iniciar_sesion_use_case,
    crear_registrar_usuario_use_case,
    crear_restablecer_contrasena_use_case,
    crear_solicitar_recuperacion_use_case,
    obtener_token_sesion,
    obtener_usuario_actual,
)
from servidor.api_rest.dependencies.servicio_dependencies import obtener_configuracion
from servidor.api_rest.schemas.inicio_sesion_entrada import InicioSesionEntrada
from servidor.api_rest.schemas.nueva_contrasena_entrada import NuevaContrasenaEntrada
from servidor.api_rest.schemas.recuperacion_entrada import RecuperacionEntrada
from servidor.api_rest.schemas.recuperacion_salida import RecuperacionSalida
from servidor.api_rest.schemas.registro_entrada import RegistroEntrada
from servidor.api_rest.schemas.usuario_salida import UsuarioSalida
from servidor.configuracion import Configuracion
from servidor.logica.commands.cerrar_sesion_command import CerrarSesionCommand
from servidor.logica.commands.iniciar_sesion_command import IniciarSesionCommand
from servidor.logica.commands.registrar_usuario_command import RegistrarUsuarioCommand
from servidor.logica.commands.restablecer_contrasena_command import RestablecerContrasenaCommand
from servidor.logica.commands.solicitar_recuperacion_command import SolicitarRecuperacionCommand
from servidor.logica.entities.usuario import Usuario
from servidor.logica.use_cases.cerrar_sesion_use_case import CerrarSesionUseCase
from servidor.logica.use_cases.iniciar_sesion_use_case import IniciarSesionUseCase
from servidor.logica.use_cases.registrar_usuario_use_case import RegistrarUsuarioUseCase
from servidor.logica.use_cases.restablecer_contrasena_use_case import RestablecerContrasenaUseCase
from servidor.logica.use_cases.solicitar_recuperacion_use_case import SolicitarRecuperacionUseCase

router = APIRouter(prefix="/api/auth", tags=["autenticación"])


@router.post("/registro", response_model=UsuarioSalida, status_code=status.HTTP_201_CREATED)
def registrar(
    datos: RegistroEntrada,
    use_case: RegistrarUsuarioUseCase = Depends(crear_registrar_usuario_use_case),
):
    return use_case.ejecutar(
        RegistrarUsuarioCommand(email=datos.email, nick=datos.nick, contrasena=datos.contrasena)
    )


@router.post("/inicio-sesion", response_model=UsuarioSalida)
def iniciar_sesion(
    datos: InicioSesionEntrada,
    response: Response,
    use_case: IniciarSesionUseCase = Depends(crear_iniciar_sesion_use_case),
    configuracion: Configuracion = Depends(obtener_configuracion),
):
    resultado = use_case.ejecutar(IniciarSesionCommand(email=datos.email, contrasena=datos.contrasena))
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
