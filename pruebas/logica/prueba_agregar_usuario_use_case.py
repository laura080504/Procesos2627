import pytest

from servidor.logica.commands import AgregarUsuarioCommand
from servidor.logica.enums import EstadoUsuario, Rol
from servidor.logica.exceptions import UsuarioYaExiste
from servidor.logica.use_cases import AgregarUsuarioUseCase


@pytest.fixture
def use_case(repositorio):
    return AgregarUsuarioUseCase(repositorio)


def prueba_agrega_usuario_con_valores_por_defecto(use_case, repositorio):
    usuario = use_case.ejecutar(AgregarUsuarioCommand(nick="laura"))
    assert usuario.rol == Rol.USUARIO
    assert usuario.estado == EstadoUsuario.ACTIVO
    assert repositorio.obtener_por_nick("laura") == usuario


def prueba_no_permite_nick_duplicado(use_case):
    use_case.ejecutar(AgregarUsuarioCommand(nick="laura"))
    with pytest.raises(UsuarioYaExiste):
        use_case.ejecutar(AgregarUsuarioCommand(nick="laura"))
