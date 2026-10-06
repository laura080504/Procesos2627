from datetime import datetime, timedelta, timezone

import pytest

from Pruebas.conftest import CONTRASENA
from Servidor.Dominio.DominioCommands.iniciar_sesion_command import IniciarSesionCommand
from Servidor.Dominio.DominioEnums.estado_usuario import EstadoUsuario
from Servidor.Dominio.DominioExceptions.credenciales_invalidas import CredencialesInvalidas
from Servidor.Dominio.DominioExceptions.cuenta_pendiente import CuentaPendiente
from Servidor.Dominio.DominioUseCases.iniciar_sesion_use_case import IniciarSesionUseCase


@pytest.fixture
def use_case(repositorio_usuarios, repositorio_sesiones, hasher):
    return IniciarSesionUseCase(repositorio_usuarios, repositorio_sesiones, hasher, timedelta(hours=1))


def prueba_inicio_correcto_crea_una_sesion(use_case, usuario_registrado, repositorio_sesiones):
    resultado = use_case.ejecutar(IniciarSesionCommand(usuario_registrado.email, CONTRASENA))
    assert resultado.usuario == usuario_registrado
    assert repositorio_sesiones.obtener(resultado.sesion.token) == resultado.sesion
    assert resultado.sesion.expira_en > datetime.now(timezone.utc)


def prueba_contrasena_incorrecta_lanza_error(use_case, usuario_registrado):
    with pytest.raises(CredencialesInvalidas):
        use_case.ejecutar(IniciarSesionCommand(usuario_registrado.email, "incorrecta"))


def prueba_email_desconocido_lanza_error(use_case):
    with pytest.raises(CredencialesInvalidas):
        use_case.ejecutar(IniciarSesionCommand("nadie@ejemplo.com", CONTRASENA))


def prueba_cuenta_pendiente_no_puede_iniciar_sesion(use_case, usuario_registrado):
    usuario_registrado.estado = EstadoUsuario.PENDIENTE
    with pytest.raises(CuentaPendiente):
        use_case.ejecutar(IniciarSesionCommand(usuario_registrado.email, CONTRASENA))
