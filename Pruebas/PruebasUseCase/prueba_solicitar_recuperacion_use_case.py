from datetime import timedelta

import pytest

from Servidor.Dominio.DominioCommands.solicitar_recuperacion_command import SolicitarRecuperacionCommand
from Servidor.Dominio.DominioExceptions.usuario_no_encontrado import UsuarioNoEncontrado
from Servidor.Dominio.DominioUseCases.solicitar_recuperacion_use_case import SolicitarRecuperacionUseCase


@pytest.fixture
def use_case(repositorio_usuarios, repositorio_recuperaciones):
    return SolicitarRecuperacionUseCase(repositorio_usuarios, repositorio_recuperaciones, timedelta(minutes=15))


def prueba_email_conocido_crea_un_token(use_case, usuario_registrado, repositorio_recuperaciones):
    recuperacion = use_case.ejecutar(SolicitarRecuperacionCommand(usuario_registrado.email))
    assert recuperacion.email == usuario_registrado.email
    assert repositorio_recuperaciones.obtener(recuperacion.token) == recuperacion


def prueba_una_nueva_solicitud_invalida_la_anterior(use_case, usuario_registrado, repositorio_recuperaciones):
    primera = use_case.ejecutar(SolicitarRecuperacionCommand(usuario_registrado.email))
    segunda = use_case.ejecutar(SolicitarRecuperacionCommand(usuario_registrado.email))
    assert repositorio_recuperaciones.obtener(primera.token) is None
    assert repositorio_recuperaciones.obtener(segunda.token) == segunda


def prueba_email_desconocido_lanza_error(use_case):
    with pytest.raises(UsuarioNoEncontrado):
        use_case.ejecutar(SolicitarRecuperacionCommand("nadie@ejemplo.com"))
