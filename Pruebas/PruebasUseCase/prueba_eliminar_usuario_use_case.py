from datetime import datetime, timedelta, timezone

import pytest

from Servidor.Dominio.DominioCommands.eliminar_usuario_command import EliminarUsuarioCommand
from Servidor.Dominio.DominioEntities.recuperacion import Recuperacion
from Servidor.Dominio.DominioEntities.sesion import Sesion
from Servidor.Dominio.DominioEntities.usuario import Usuario
from Servidor.Dominio.DominioEnums.estado_usuario import EstadoUsuario
from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Dominio.DominioExceptions.permiso_insuficiente import PermisoInsuficiente
from Servidor.Dominio.DominioExceptions.usuario_no_encontrado import UsuarioNoEncontrado
from Servidor.Dominio.DominioUseCases.eliminar_usuario_use_case import EliminarUsuarioUseCase


@pytest.fixture
def use_case(repositorio_usuarios, repositorio_sesiones, repositorio_recuperaciones):
    return EliminarUsuarioUseCase(repositorio_usuarios, repositorio_sesiones, repositorio_recuperaciones)


def prueba_elimina_usuario_y_sus_sesiones(use_case, usuario_registrado, repositorio_usuarios, repositorio_sesiones):
    sesion = Sesion("token", usuario_registrado.email, datetime.now(timezone.utc) + timedelta(hours=1))
    repositorio_sesiones.guardar(sesion)

    use_case.ejecutar(
        EliminarUsuarioCommand(usuario_registrado.email, usuario_registrado.email, Rol.USUARIO)
    )

    assert repositorio_usuarios.obtener_por_email(usuario_registrado.email).estado == EstadoUsuario.ELIMINADO
    assert repositorio_sesiones.obtener("token") is None


def prueba_elimina_tambien_las_recuperaciones(
    use_case, usuario_registrado, repositorio_recuperaciones
):
    repositorio_recuperaciones.guardar(
        Recuperacion("token-recuperacion", usuario_registrado.email, datetime.now(timezone.utc) + timedelta(hours=1))
    )
    use_case.ejecutar(
        EliminarUsuarioCommand(usuario_registrado.email, usuario_registrado.email, Rol.USUARIO)
    )
    assert repositorio_recuperaciones.obtener("token-recuperacion") is None


def prueba_eliminar_inexistente_lanza_error(use_case):
    with pytest.raises(UsuarioNoEncontrado):
        use_case.ejecutar(EliminarUsuarioCommand("nadie@ejemplo.com", "admin@ejemplo.com", Rol.PROFESOR))


def prueba_un_usuario_no_elimina_a_otro(use_case, usuario_registrado, repositorio_usuarios, hasher):
    otro = repositorio_usuarios.insertar(
        Usuario(email="otro@ejemplo.com", nick="otro", contrasena_hash=hasher.hashear("contrasena-segura"))
    )
    with pytest.raises(PermisoInsuficiente):
        use_case.ejecutar(EliminarUsuarioCommand(otro.email, usuario_registrado.email, Rol.USUARIO))
    assert repositorio_usuarios.obtener_por_email(otro.email) is not None


def prueba_un_profesor_elimina_a_un_alumno(use_case, usuario_registrado, repositorio_usuarios):
    use_case.ejecutar(EliminarUsuarioCommand(usuario_registrado.email, "profe@ejemplo.com", Rol.PROFESOR))
    assert repositorio_usuarios.obtener_por_email(usuario_registrado.email).estado == EstadoUsuario.ELIMINADO


def prueba_un_profesor_no_elimina_a_otro_profesor(use_case, repositorio_usuarios, hasher):
    profesor = repositorio_usuarios.insertar(
        Usuario(
            email="profe@ejemplo.com",
            nick="profe",
            contrasena_hash=hasher.hashear("contrasena-segura"),
            rol=Rol.PROFESOR,
        )
    )
    with pytest.raises(PermisoInsuficiente):
        use_case.ejecutar(EliminarUsuarioCommand(profesor.email, "otro-profe@ejemplo.com", Rol.PROFESOR))
    assert repositorio_usuarios.obtener_por_email(profesor.email).estado == EstadoUsuario.ACTIVO


def prueba_el_superadministrador_elimina_a_un_profesor(use_case, repositorio_usuarios, hasher):
    profesor = repositorio_usuarios.insertar(
        Usuario(
            email="profe@ejemplo.com",
            nick="profe",
            contrasena_hash=hasher.hashear("contrasena-segura"),
            rol=Rol.PROFESOR,
        )
    )
    use_case.ejecutar(
        EliminarUsuarioCommand(profesor.email, "super@ejemplo.com", Rol.SUPERADMINISTRADOR)
    )
    assert repositorio_usuarios.obtener_por_email(profesor.email).estado == EstadoUsuario.ELIMINADO


def prueba_nadie_elimina_al_superadministrador(use_case, repositorio_usuarios, hasher):
    superadmin = repositorio_usuarios.insertar(
        Usuario(
            email="super@ejemplo.com",
            nick="super",
            contrasena_hash=hasher.hashear("contrasena-segura"),
            rol=Rol.SUPERADMINISTRADOR,
        )
    )
    with pytest.raises(PermisoInsuficiente):
        use_case.ejecutar(
            EliminarUsuarioCommand(superadmin.email, superadmin.email, Rol.SUPERADMINISTRADOR)
        )
    assert repositorio_usuarios.obtener_por_email(superadmin.email).estado == EstadoUsuario.ACTIVO
