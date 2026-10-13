import pytest

from Servidor.Dominio.DominioCommands.asignar_administrador_command import AsignarAdministradorCommand
from Servidor.Dominio.DominioEnums.estado_usuario import EstadoUsuario
from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Dominio.DominioExceptions.usuario_no_encontrado import UsuarioNoEncontrado
from Servidor.Dominio.DominioUseCases.asignar_administrador_use_case import AsignarAdministradorUseCase


@pytest.fixture
def use_case(repositorio_usuarios):
    return AsignarAdministradorUseCase(repositorio_usuarios)


def prueba_convierte_usuario_en_administrador(use_case, usuario_registrado, repositorio_usuarios):
    actualizado = use_case.ejecutar(
        AsignarAdministradorCommand(usuario_registrado.email, "admin@ejemplo.com")
    )
    guardado = repositorio_usuarios.obtener_por_email(usuario_registrado.email)
    assert actualizado.rol == Rol.ADMINISTRADOR
    assert guardado.rol == Rol.ADMINISTRADOR


def prueba_eliminado_no_puede_ser_administrador(use_case, usuario_registrado, repositorio_usuarios):
    usuario_registrado.estado = EstadoUsuario.ELIMINADO
    repositorio_usuarios.actualizar(usuario_registrado)
    with pytest.raises(UsuarioNoEncontrado):
        use_case.ejecutar(AsignarAdministradorCommand(usuario_registrado.email, "admin@ejemplo.com"))
    assert repositorio_usuarios.obtener_por_email(usuario_registrado.email).rol == Rol.USUARIO


def prueba_inexistente_lanza_error(use_case):
    with pytest.raises(UsuarioNoEncontrado):
        use_case.ejecutar(AsignarAdministradorCommand("nadie@ejemplo.com", "admin@ejemplo.com"))
