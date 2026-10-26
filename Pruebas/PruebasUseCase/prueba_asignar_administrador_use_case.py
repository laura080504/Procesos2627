import pytest

from Servidor.Dominio.DominioCommands.asignar_administrador_command import AsignarAdministradorCommand
from Servidor.Dominio.DominioEnums.estado_usuario import EstadoUsuario
from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Dominio.DominioExceptions.permiso_insuficiente import PermisoInsuficiente
from Servidor.Dominio.DominioExceptions.usuario_no_encontrado import UsuarioNoEncontrado
from Servidor.Dominio.DominioUseCases.asignar_administrador_use_case import AsignarAdministradorUseCase


@pytest.fixture
def use_case(repositorio_usuarios):
    return AsignarAdministradorUseCase(repositorio_usuarios)


def _orden(email):
    return AsignarAdministradorCommand(email, "super@ejemplo.com", Rol.SUPERADMINISTRADOR)


def prueba_el_superadministrador_convierte_un_alumno_en_profesor(use_case, usuario_registrado, repositorio_usuarios):
    actualizado = use_case.ejecutar(_orden(usuario_registrado.email))
    guardado = repositorio_usuarios.obtener_por_email(usuario_registrado.email)
    assert actualizado.rol == Rol.PROFESOR
    assert guardado.rol == Rol.PROFESOR


def prueba_un_profesor_no_asigna_el_cargo(use_case, usuario_registrado):
    with pytest.raises(PermisoInsuficiente):
        use_case.ejecutar(
            AsignarAdministradorCommand(usuario_registrado.email, "profe@ejemplo.com", Rol.PROFESOR)
        )


def prueba_eliminado_no_puede_ser_profesor(use_case, usuario_registrado, repositorio_usuarios):
    usuario_registrado.estado = EstadoUsuario.ELIMINADO
    repositorio_usuarios.actualizar(usuario_registrado)
    with pytest.raises(UsuarioNoEncontrado):
        use_case.ejecutar(_orden(usuario_registrado.email))
    assert repositorio_usuarios.obtener_por_email(usuario_registrado.email).rol == Rol.USUARIO


def prueba_inexistente_lanza_error(use_case):
    with pytest.raises(UsuarioNoEncontrado):
        use_case.ejecutar(_orden("nadie@ejemplo.com"))
