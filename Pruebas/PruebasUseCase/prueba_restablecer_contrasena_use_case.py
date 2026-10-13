from datetime import datetime, timedelta, timezone

import pytest

from Pruebas.conftest import CONTRASENA
from Servidor.Dominio.DominioCommands.iniciar_sesion_command import IniciarSesionCommand
from Servidor.Dominio.DominioCommands.restablecer_contrasena_command import RestablecerContrasenaCommand
from Servidor.Dominio.DominioEntities.recuperacion import Recuperacion
from Servidor.Dominio.DominioEnums.estado_usuario import EstadoUsuario
from Servidor.Dominio.DominioExceptions.cuenta_eliminada import CuentaEliminada
from Servidor.Dominio.DominioExceptions.recuperacion_no_valida import RecuperacionNoValida
from Servidor.Dominio.DominioUseCases.iniciar_sesion_use_case import IniciarSesionUseCase
from Servidor.Dominio.DominioUseCases.restablecer_contrasena_use_case import RestablecerContrasenaUseCase

NUEVA = "nueva-segura"


@pytest.fixture
def use_case(repositorio_usuarios, repositorio_recuperaciones, repositorio_sesiones, hasher):
    return RestablecerContrasenaUseCase(
        repositorio_usuarios, repositorio_recuperaciones, repositorio_sesiones, hasher
    )


def prueba_cambia_la_contrasena_y_gasta_el_token(
    use_case, usuario_registrado, repositorio_usuarios, repositorio_recuperaciones, hasher
):
    hash_anterior = usuario_registrado.contrasena_hash
    recuperacion = repositorio_recuperaciones.guardar(
        Recuperacion("token-valido", usuario_registrado.email, datetime.now(timezone.utc) + timedelta(minutes=15))
    )
    use_case.ejecutar(RestablecerContrasenaCommand(recuperacion.token, NUEVA))
    guardado = repositorio_usuarios.obtener_por_email(usuario_registrado.email)
    assert hasher.verificar(NUEVA, guardado.contrasena_hash)
    assert not hasher.verificar(CONTRASENA, guardado.contrasena_hash)
    assert guardado.contrasena_hash != hash_anterior
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


def prueba_usuario_eliminado_no_cambia_la_contrasena(
    use_case, usuario_registrado, repositorio_usuarios, repositorio_recuperaciones, hasher
):
    hash_anterior = usuario_registrado.contrasena_hash
    usuario_registrado.estado = EstadoUsuario.ELIMINADO
    repositorio_usuarios.actualizar(usuario_registrado)
    repositorio_recuperaciones.guardar(
        Recuperacion("token-valido", usuario_registrado.email, datetime.now(timezone.utc) + timedelta(minutes=15))
    )
    with pytest.raises(CuentaEliminada, match="no puedes recuperar la contraseña"):
        use_case.ejecutar(RestablecerContrasenaCommand("token-valido", NUEVA))
    guardado = repositorio_usuarios.obtener_por_email(usuario_registrado.email)
    assert guardado.contrasena_hash == hash_anterior
    assert hasher.verificar(CONTRASENA, guardado.contrasena_hash)
    assert repositorio_recuperaciones.obtener("token-valido") is None
