from datetime import datetime, timedelta, timezone

import pytest

from Servidor.Dominio.DominioEntities.confirmacion import Confirmacion
from Servidor.Dominio.DominioEntities.usuario import Usuario
from Servidor.Dominio.DominioEnums.estado_usuario import EstadoUsuario
from Servidor.Dominio.DominioExceptions.confirmacion_no_valida import ConfirmacionNoValida
from Servidor.Dominio.DominioExceptions.correo_no_enviado import CorreoNoEnviado
from Servidor.Dominio.DominioExceptions.cuenta_eliminada import CuentaEliminada
from Servidor.Dominio.DominioExceptions.cuenta_ya_activa import CuentaYaActiva
from Servidor.Dominio.DominioExceptions.oauth_no_valido import OauthNoValido
from Servidor.Dominio.DominioUseCases.confirmar_cuenta_use_case import ConfirmarCuentaUseCase
from Servidor.Dominio.DominioUseCases.emitir_confirmacion_use_case import EmitirConfirmacionUseCase
from Servidor.Dominio.DominioUseCases.iniciar_sesion_google_use_case import IniciarSesionGoogleUseCase
from Servidor.Infraestructura.enviador_correo_memoria import EnviadorCorreoMemoria


def prueba_confirmar_activa_la_cuenta_y_gasta_el_token(repositorio_usuarios, repositorio_confirmaciones, hasher):
    repositorio_usuarios.insertar(
        Usuario(email="laura@ejemplo.com", nick="laura", contrasena_hash=hasher.hashear("contrasena-segura"), estado=EstadoUsuario.PENDIENTE)
    )
    repositorio_confirmaciones.guardar(
        Confirmacion("token-ok", "laura@ejemplo.com", datetime.now(timezone.utc) + timedelta(hours=1))
    )
    usuario = ConfirmarCuentaUseCase(repositorio_usuarios, repositorio_confirmaciones).ejecutar("token-ok")
    assert usuario.estado == EstadoUsuario.ACTIVO
    assert repositorio_confirmaciones.obtener("token-ok") is None


def prueba_un_enlace_caducado_no_confirma(repositorio_usuarios, repositorio_confirmaciones, hasher):
    repositorio_usuarios.insertar(
        Usuario(email="laura@ejemplo.com", nick="laura", contrasena_hash="hash", estado=EstadoUsuario.PENDIENTE)
    )
    repositorio_confirmaciones.guardar(
        Confirmacion("token-viejo", "laura@ejemplo.com", datetime.now(timezone.utc) - timedelta(minutes=1))
    )
    with pytest.raises(ConfirmacionNoValida):
        ConfirmarCuentaUseCase(repositorio_usuarios, repositorio_confirmaciones).ejecutar("token-viejo")
    assert repositorio_usuarios.obtener_por_email("laura@ejemplo.com").estado == EstadoUsuario.PENDIENTE


def prueba_no_reenvia_si_la_cuenta_ya_esta_activa(repositorio_usuarios, repositorio_confirmaciones, usuario_registrado):
    emitir = EmitirConfirmacionUseCase(
        repositorio_usuarios, repositorio_confirmaciones, EnviadorCorreoMemoria(), timedelta(hours=24)
    )
    with pytest.raises(CuentaYaActiva):
        emitir.ejecutar(usuario_registrado.email, "http://localhost")


def prueba_si_brevo_falla_borra_el_token(repositorio_usuarios, repositorio_confirmaciones, hasher):
    repositorio_usuarios.insertar(
        Usuario(email="laura@ejemplo.com", nick="laura", contrasena_hash="hash", estado=EstadoUsuario.PENDIENTE)
    )

    class EnviadorQueFalla:
        def enviar(self, destino, asunto, cuerpo):
            raise CorreoNoEnviado()

    emitir = EmitirConfirmacionUseCase(
        repositorio_usuarios, repositorio_confirmaciones, EnviadorQueFalla(), timedelta(hours=24)
    )
    with pytest.raises(CorreoNoEnviado):
        emitir.ejecutar("laura@ejemplo.com", "http://localhost")
    assert repositorio_confirmaciones._confirmaciones == {}


def prueba_google_activa_una_cuenta_pendiente(repositorio_usuarios, repositorio_sesiones, repositorio_confirmaciones, hasher):
    repositorio_usuarios.insertar(
        Usuario(email="laura@ejemplo.com", nick="laura", contrasena_hash=hasher.hashear("contrasena-segura"), estado=EstadoUsuario.PENDIENTE)
    )
    repositorio_confirmaciones.guardar(
        Confirmacion("token-ok", "laura@ejemplo.com", datetime.now(timezone.utc) + timedelta(hours=1))
    )
    use_case = IniciarSesionGoogleUseCase(
        repositorio_usuarios, repositorio_sesiones, hasher, timedelta(hours=1), repositorio_confirmaciones
    )
    resultado = use_case.ejecutar("laura@ejemplo.com", "Laura")
    assert resultado.usuario.estado == EstadoUsuario.ACTIVO
    assert hasher.verificar("contrasena-segura", resultado.usuario.contrasena_hash)
    assert repositorio_confirmaciones.obtener("token-ok") is None
    assert repositorio_sesiones.obtener(resultado.sesion.token).email == "laura@ejemplo.com"


def prueba_google_rechaza_una_cuenta_eliminada(repositorio_usuarios, repositorio_sesiones, hasher):
    repositorio_usuarios.insertar(
        Usuario(email="laura@ejemplo.com", nick="laura", contrasena_hash="hash", estado=EstadoUsuario.ELIMINADO)
    )
    use_case = IniciarSesionGoogleUseCase(repositorio_usuarios, repositorio_sesiones, hasher, timedelta(hours=1))
    with pytest.raises(CuentaEliminada):
        use_case.ejecutar("laura@ejemplo.com", "Laura")


def prueba_google_sin_email_no_crea_usuario(repositorio_usuarios, repositorio_sesiones, hasher):
    use_case = IniciarSesionGoogleUseCase(repositorio_usuarios, repositorio_sesiones, hasher, timedelta(hours=1))
    with pytest.raises(OauthNoValido):
        use_case.ejecutar("sin-arroba", "Laura")
    assert repositorio_usuarios.obtener_todos() == []
