from datetime import datetime, timedelta, timezone

import pytest

from servidor.dominio.commands.eliminar_usuario_command import EliminarUsuarioCommand
from servidor.dominio.entities.sesion import Sesion
from servidor.dominio.entities.usuario import Usuario
from servidor.dominio.enums.rol import Rol
from servidor.dominio.exceptions.permiso_insuficiente import PermisoInsuficiente
from servidor.dominio.exceptions.usuario_no_encontrado import UsuarioNoEncontrado
from servidor.dominio.use_cases.eliminar_usuario_use_case import EliminarUsuarioUseCase


@pytest.fixture
def use_case(repositorio_usuarios, repositorio_sesiones):
    return EliminarUsuarioUseCase(repositorio_usuarios, repositorio_sesiones)


def prueba_elimina_usuario_y_sus_sesiones(use_case, usuario_registrado, repositorio_usuarios, repositorio_sesiones):
    sesion = Sesion("token", usuario_registrado.email, datetime.now(timezone.utc) + timedelta(hours=1))
    repositorio_sesiones.guardar(sesion)

    use_case.ejecutar(
        EliminarUsuarioCommand(usuario_registrado.email, usuario_registrado.email, Rol.USUARIO)
    )

    assert repositorio_usuarios.obtener_por_email(usuario_registrado.email) is None
    assert repositorio_sesiones.obtener("token") is None


def prueba_eliminar_inexistente_lanza_error(use_case):
    with pytest.raises(UsuarioNoEncontrado):
        use_case.ejecutar(EliminarUsuarioCommand("nadie@ejemplo.com", "admin@ejemplo.com", Rol.ADMINISTRADOR))


def prueba_un_usuario_no_elimina_a_otro(use_case, usuario_registrado, repositorio_usuarios, hasher):
    otro = repositorio_usuarios.insertar(
        Usuario(email="otro@ejemplo.com", nick="otro", contrasena_hash=hasher.hashear("contrasena-segura"))
    )
    with pytest.raises(PermisoInsuficiente):
        use_case.ejecutar(EliminarUsuarioCommand(otro.email, usuario_registrado.email, Rol.USUARIO))
    assert repositorio_usuarios.obtener_por_email(otro.email) is not None
