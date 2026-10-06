from datetime import datetime, timedelta, timezone

import pytest

from servidor.dominio.commands.eliminar_usuario_command import EliminarUsuarioCommand
from servidor.dominio.entities.sesion import Sesion
from servidor.dominio.exceptions.usuario_no_encontrado import UsuarioNoEncontrado
from servidor.dominio.use_cases.eliminar_usuario_use_case import EliminarUsuarioUseCase


@pytest.fixture
def use_case(repositorio_usuarios, repositorio_sesiones):
    return EliminarUsuarioUseCase(repositorio_usuarios, repositorio_sesiones)


def prueba_elimina_usuario_y_sus_sesiones(use_case, usuario_registrado, repositorio_usuarios, repositorio_sesiones):
    sesion = Sesion("token", usuario_registrado.email, datetime.now(timezone.utc) + timedelta(hours=1))
    repositorio_sesiones.guardar(sesion)

    use_case.ejecutar(EliminarUsuarioCommand(usuario_registrado.email))

    assert repositorio_usuarios.obtener_por_email(usuario_registrado.email) is None
    assert repositorio_sesiones.obtener("token") is None


def prueba_eliminar_inexistente_lanza_error(use_case):
    with pytest.raises(UsuarioNoEncontrado):
        use_case.ejecutar(EliminarUsuarioCommand("nadie@ejemplo.com"))
