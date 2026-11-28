import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import RedirectResponse

from Servidor.ApiRest.ApiRestDependencies.auth_dependencies import (
    crear_cerrar_sesion_use_case,
    crear_confirmar_cuenta_use_case,
    crear_emitir_confirmacion_use_case,
    crear_iniciar_sesion_google_use_case,
    crear_iniciar_sesion_uclm_use_case,
    crear_iniciar_sesion_use_case,
    crear_registrar_usuario_use_case,
    crear_restablecer_contrasena_use_case,
    crear_solicitar_recuperacion_use_case,
    obtener_cliente_google,
    obtener_cliente_uclm,
    obtener_token_sesion,
    obtener_usuario_actual,
)
from Servidor.ApiRest.ApiRestDependencies.configuracion_dependencies import obtener_configuracion
from Servidor.ApiRest.ApiRestSchemas.confirmar_entrada import ConfirmarEntrada
from Servidor.ApiRest.ApiRestSchemas.inicio_sesion_entrada import InicioSesionEntrada
from Servidor.ApiRest.ApiRestSchemas.nueva_contrasena_entrada import NuevaContrasenaEntrada
from Servidor.ApiRest.ApiRestSchemas.recuperacion_entrada import RecuperacionEntrada
from Servidor.ApiRest.ApiRestSchemas.recuperacion_salida import RecuperacionSalida
from Servidor.ApiRest.ApiRestSchemas.registro_entrada import RegistroEntrada
from Servidor.ApiRest.ApiRestSchemas.usuario_salida import UsuarioSalida
from Servidor.configuracion import Configuracion
from Servidor.Dominio.DominioCommands.cerrar_sesion_command import CerrarSesionCommand
from Servidor.Dominio.DominioCommands.iniciar_sesion_command import IniciarSesionCommand
from Servidor.Dominio.DominioCommands.registrar_usuario_command import RegistrarUsuarioCommand
from Servidor.Dominio.DominioCommands.restablecer_contrasena_command import RestablecerContrasenaCommand
from Servidor.Dominio.DominioCommands.solicitar_recuperacion_command import SolicitarRecuperacionCommand
from Servidor.Dominio.DominioEntities.usuario import Usuario
from Servidor.Dominio.DominioExceptions.cuenta_eliminada import CuentaEliminada
from Servidor.Dominio.DominioExceptions.cuenta_pendiente import CuentaPendiente
from Servidor.Dominio.DominioExceptions.oauth_no_valido import OauthNoValido
from Servidor.Dominio.DominioServices.token_seguro import generar_pkce
from Servidor.Dominio.DominioUseCases.cerrar_sesion_use_case import CerrarSesionUseCase
from Servidor.Dominio.DominioUseCases.confirmar_cuenta_use_case import ConfirmarCuentaUseCase
from Servidor.Dominio.DominioUseCases.emitir_confirmacion_use_case import EmitirConfirmacionUseCase
from Servidor.Dominio.DominioUseCases.iniciar_sesion_google_use_case import IniciarSesionGoogleUseCase
from Servidor.Dominio.DominioUseCases.iniciar_sesion_use_case import IniciarSesionUseCase
from Servidor.Dominio.DominioUseCases.registrar_usuario_use_case import RegistrarUsuarioUseCase
from Servidor.Dominio.DominioUseCases.restablecer_contrasena_use_case import RestablecerContrasenaUseCase
from Servidor.Dominio.DominioUseCases.solicitar_recuperacion_use_case import SolicitarRecuperacionUseCase
from Servidor.Infraestructura.cliente_google import ClienteGoogle
from Servidor.Infraestructura.cliente_uclm import ClienteUclm
from Servidor.Infraestructura.registro_actividad import registro_actividad

router = APIRouter(prefix="/api/auth", tags=["autenticación"])
COOKIE_OAUTH = "oauth_estado"
COOKIE_PKCE = "oauth_pkce"


def _url_base(request: Request, configuracion: Configuracion) -> str:
    if configuracion.url_publica:
        return configuracion.url_publica
    return str(request.base_url).rstrip("/")


def _poner_sesion(
    response: Response,
    token: str,
    configuracion: Configuracion,
    max_age_segundos: int | None = None,
) -> None:
    kwargs = {
        "key": configuracion.nombre_cookie_sesion,
        "value": token,
        "httponly": True,
        "secure": configuracion.cookie_segura,
        "samesite": "lax",
        "path": "/",
    }
    if max_age_segundos is not None:
        kwargs["max_age"] = max_age_segundos
    response.set_cookie(**kwargs)


def _quitar_cookie(response: Response, nombre: str, configuracion: Configuracion) -> None:
    response.delete_cookie(
        key=nombre,
        path="/",
        secure=configuracion.cookie_segura,
        httponly=True,
        samesite="lax",
    )


def _estado_oauth_valido(state: str, estado_cookie: str) -> bool:
    if not state or not estado_cookie:
        return False
    return secrets.compare_digest(state, estado_cookie)


def _poner_oauth(respuesta: Response, estado: str, verifier: str, configuracion: Configuracion) -> None:
    comunes = {
        "max_age": 600,
        "httponly": True,
        "secure": configuracion.cookie_segura,
        "samesite": "lax",
        "path": "/",
    }
    respuesta.set_cookie(key=COOKIE_OAUTH, value=estado, **comunes)
    respuesta.set_cookie(key=COOKIE_PKCE, value=verifier, **comunes)


def _email_verificado(perfil: dict) -> bool:
    if "email_verified" not in perfil:
        return False
    valor = perfil.get("email_verified")
    return valor is True or valor == "true" or valor == 1


@router.post("/registro", response_model=UsuarioSalida, status_code=status.HTTP_201_CREATED)
def registrar(
    datos: RegistroEntrada,
    request: Request,
    use_case: RegistrarUsuarioUseCase = Depends(crear_registrar_usuario_use_case),
    configuracion: Configuracion = Depends(obtener_configuracion),
):
    usuario = use_case.ejecutar(
        RegistrarUsuarioCommand(
            email=datos.email,
            nick=datos.nick,
            contrasena=datos.contrasena,
            url_base=_url_base(request, configuracion),
        )
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
    resultado = use_case.ejecutar(
        IniciarSesionCommand(email=datos.email, contrasena=datos.contrasena, recordar=datos.recordar)
    )
    registro_actividad.inicio(resultado.usuario.email)
    max_age = int((resultado.sesion.expira_en - datetime.now(timezone.utc)).total_seconds())
    _poner_sesion(response, resultado.sesion.token, configuracion, max(60, max_age))
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
    _quitar_cookie(response, configuracion.nombre_cookie_sesion, configuracion)


@router.get("/sesion", response_model=UsuarioSalida)
def obtener_sesion(usuario: Usuario = Depends(obtener_usuario_actual)):
    return usuario


@router.post("/recuperacion", response_model=RecuperacionSalida)
def solicitar_recuperacion(
    datos: RecuperacionEntrada,
    request: Request,
    use_case: SolicitarRecuperacionUseCase = Depends(crear_solicitar_recuperacion_use_case),
    configuracion: Configuracion = Depends(obtener_configuracion),
):
    use_case.ejecutar(
        SolicitarRecuperacionCommand(email=datos.email),
        _url_base(request, configuracion),
    )
    return RecuperacionSalida()


@router.post("/nueva-contrasena", status_code=status.HTTP_204_NO_CONTENT)
def restablecer_contrasena(
    datos: NuevaContrasenaEntrada,
    use_case: RestablecerContrasenaUseCase = Depends(crear_restablecer_contrasena_use_case),
):
    use_case.ejecutar(RestablecerContrasenaCommand(token=datos.token, contrasena=datos.contrasena))


@router.post("/confirmar", response_model=UsuarioSalida)
def confirmar_cuenta(
    datos: ConfirmarEntrada,
    use_case: ConfirmarCuentaUseCase = Depends(crear_confirmar_cuenta_use_case),
):
    usuario = use_case.ejecutar(datos.token)
    registro_actividad.confirmacion(usuario.email)
    return usuario


@router.post("/reenviar-confirmacion", status_code=status.HTTP_204_NO_CONTENT)
def reenviar_confirmacion(
    datos: RecuperacionEntrada,
    request: Request,
    use_case: EmitirConfirmacionUseCase = Depends(crear_emitir_confirmacion_use_case),
    configuracion: Configuracion = Depends(obtener_configuracion),
):
    use_case.ejecutar(datos.email, _url_base(request, configuracion))


@router.get("/google")
def iniciar_google(
    request: Request,
    cliente_google: ClienteGoogle = Depends(obtener_cliente_google),
    configuracion: Configuracion = Depends(obtener_configuracion),
):
    if not configuracion.google_client_id or not configuracion.google_client_secret:
        return RedirectResponse("/?aviso=google-no-configurado", status_code=status.HTTP_302_FOUND)
    estado = secrets.token_urlsafe(24)
    verifier, challenge = generar_pkce()
    destino = cliente_google.url_autorizacion(
        configuracion.google_client_id,
        f"{_url_base(request, configuracion)}/api/auth/google/callback",
        estado,
        challenge,
    )
    respuesta = RedirectResponse(destino, status_code=status.HTTP_302_FOUND)
    _poner_oauth(respuesta, estado, verifier, configuracion)
    return respuesta


@router.get("/google/callback")
def callback_google(
    request: Request,
    code: str = "",
    state: str = "",
    cliente_google: ClienteGoogle = Depends(obtener_cliente_google),
    use_case: IniciarSesionGoogleUseCase = Depends(crear_iniciar_sesion_google_use_case),
    configuracion: Configuracion = Depends(obtener_configuracion),
):
    def volver(aviso: str) -> RedirectResponse:
        respuesta = RedirectResponse(f"/?aviso={aviso}", status_code=status.HTTP_302_FOUND)
        _quitar_cookie(respuesta, COOKIE_OAUTH, configuracion)
        _quitar_cookie(respuesta, COOKIE_PKCE, configuracion)
        return respuesta

    estado_cookie = request.cookies.get(COOKIE_OAUTH, "")
    verifier = request.cookies.get(COOKIE_PKCE, "")
    if not code or not _estado_oauth_valido(state, estado_cookie) or not verifier:
        return volver("google-error")
    if not configuracion.google_client_id or not configuracion.google_client_secret:
        return volver("google-no-configurado")
    try:
        perfil = cliente_google.perfil(
            code,
            f"{_url_base(request, configuracion)}/api/auth/google/callback",
            configuracion.google_client_id,
            configuracion.google_client_secret,
            verifier,
        )
        resultado = use_case.ejecutar(
            perfil.get("email", ""),
            perfil.get("name", ""),
            email_verificado=_email_verificado(perfil),
        )
    except CuentaEliminada:
        return volver("cuenta-eliminada")
    except CuentaPendiente:
        return volver("cuenta-pendiente")
    except OauthNoValido:
        return volver("google-error")
    registro_actividad.inicio(resultado.usuario.email)
    respuesta = RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    max_age = int(configuracion.duracion_sesion.total_seconds())
    _poner_sesion(respuesta, resultado.sesion.token, configuracion, max_age)
    _quitar_cookie(respuesta, COOKIE_OAUTH, configuracion)
    _quitar_cookie(respuesta, COOKIE_PKCE, configuracion)
    return respuesta


@router.get("/uclm")
def iniciar_uclm(
    request: Request,
    cliente_uclm: ClienteUclm = Depends(obtener_cliente_uclm),
    configuracion: Configuracion = Depends(obtener_configuracion),
):
    if not configuracion.uclm_client_id or not configuracion.uclm_client_secret:
        return RedirectResponse("/?aviso=uclm-no-configurado", status_code=status.HTTP_302_FOUND)
    estado = secrets.token_urlsafe(24)
    verifier, challenge = generar_pkce()
    destino = cliente_uclm.url_autorizacion(
        configuracion.uclm_client_id,
        f"{_url_base(request, configuracion)}/api/auth/uclm/callback",
        estado,
        challenge,
    )
    respuesta = RedirectResponse(destino, status_code=status.HTTP_302_FOUND)
    _poner_oauth(respuesta, estado, verifier, configuracion)
    return respuesta


@router.get("/uclm/callback")
def callback_uclm(
    request: Request,
    code: str = "",
    state: str = "",
    cliente_uclm: ClienteUclm = Depends(obtener_cliente_uclm),
    use_case: IniciarSesionGoogleUseCase = Depends(crear_iniciar_sesion_uclm_use_case),
    configuracion: Configuracion = Depends(obtener_configuracion),
):
    def volver(aviso: str) -> RedirectResponse:
        respuesta = RedirectResponse(f"/?aviso={aviso}", status_code=status.HTTP_302_FOUND)
        _quitar_cookie(respuesta, COOKIE_OAUTH, configuracion)
        _quitar_cookie(respuesta, COOKIE_PKCE, configuracion)
        return respuesta

    estado_cookie = request.cookies.get(COOKIE_OAUTH, "")
    verifier = request.cookies.get(COOKIE_PKCE, "")
    if not code or not _estado_oauth_valido(state, estado_cookie) or not verifier:
        return volver("uclm-error")
    if not configuracion.uclm_client_id or not configuracion.uclm_client_secret:
        return volver("uclm-no-configurado")
    try:
        perfil = cliente_uclm.perfil(
            code,
            f"{_url_base(request, configuracion)}/api/auth/uclm/callback",
            configuracion.uclm_client_id,
            configuracion.uclm_client_secret,
            verifier,
        )
        email = perfil.get("email") or perfil.get("mail") or perfil.get("upn") or ""
        nombre = perfil.get("name") or perfil.get("nombre") or perfil.get("preferred_username") or ""
        resultado = use_case.ejecutar(email, nombre, email_verificado=_email_verificado(perfil))
    except CuentaEliminada:
        return volver("cuenta-eliminada")
    except CuentaPendiente:
        return volver("cuenta-pendiente")
    except OauthNoValido:
        return volver("uclm-error")
    registro_actividad.inicio(resultado.usuario.email)
    respuesta = RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    max_age = int(configuracion.duracion_sesion.total_seconds())
    _poner_sesion(respuesta, resultado.sesion.token, configuracion, max_age)
    _quitar_cookie(respuesta, COOKIE_OAUTH, configuracion)
    _quitar_cookie(respuesta, COOKIE_PKCE, configuracion)
    return respuesta
