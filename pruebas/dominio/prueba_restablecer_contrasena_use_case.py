from datetime import datetime, timedelta, timezone

import pytest

from pruebas.conftest import CONTRASENA
from servidor.dominio.commands.iniciar_sesion_command import IniciarSesionCommand
from servidor.dominio.commands.restablecer_contrasena_command import RestablecerContrasenaCommand
from servidor.dominio.entities.recuperacion import Recuperacion
from servidor.dominio.exceptions.recuperacion_no_valida import RecuperacionNoValida
from servidor.dominio.use_cases.iniciar_sesion_use_case import IniciarSesionUseCase
from servidor.dominio.use_cases.restablecer_contrasena_use_case import RestablecerContrasenaUseCase

NUEVA = "nueva-segura"


@pytest.fixture
def use_case(repositorio_usuarios, repositorio_recuperaciones, repositorio_sesiones, hasher):
    return RestablecerContrasenaUseCase(
        repositorio_usuarios, repositorio_recuperaciones, repositorio_sesiones, hasher
    )


def prueba_cambia_la_contrasena_y_gasta_el_token(
    use_case, usuario_registrado, repositorio_recuperaciones, hasher
):
    recuperacion = repositorio_recuperaciones.guardar(
        Recuperacion("token-valido", usuario_registrado.email, datetime.now(timezone.utc) + timedelta(minutes=15))
    )
    use_case.ejecutar(RestablecerContrasenaCommand(recuperacion.token, NUEVA))
    assert hasher.verificar(NUEVA, usuario_registrado.contrasena_hash)
    assert repositorio_recuperaciones.obtener(recuperacion.token) is None
    with pytest.raises(RecuperacionNoValida):
        use_case.ejecutar(RestablecerContrasenaCommand(recuperacion.token, NUEVA))


def prueba_invalida_las_sesiones_abiertas(
    use_case, usuario_registrado, repositorio_usuarios, repositorio_sesiones, repositorio_recuperaciones, hasher
):
    sesion = IniciarSesionUseCase(
        repositorio_usuarios, repositorio_sesiones, hasher, timedelta(hours=1)
    ).ejecutar(IniciarSesionCommand(usuario_registrado.email, CONTRASENA)).sesion
    repositorio_recuperaciones.guardar(
        Recuperacion("token-valido", usuario_registrado.email, datetime.now(timezone.utc) + timedelta(minutes=15))
    )
    use_case.ejecutar(RestablecerContrasenaCommand("token-valido", NUEVA))
    assert repositorio_sesiones.obtener(sesion.token) is None


def prueba_token_desconocido_lanza_error(use_case):
    with pytest.raises(RecuperacionNoValida):
        use_case.ejecutar(RestablecerContrasenaCommand("no-existe", NUEVA))


def prueba_token_caducado_lanza_error(use_case, usuario_registrado, repositorio_recuperaciones):
    repositorio_recuperaciones.guardar(
        Recuperacion("token-viejo", usuario_registrado.email, datetime.now(timezone.utc) - timedelta(minutes=1))
    )
    with pytest.raises(RecuperacionNoValida):
        use_case.ejecutar(RestablecerContrasenaCommand("token-viejo", NUEVA))
    assert repositorio_recuperaciones.obtener("token-viejo") is None
