import pytest

from servidor.logica.commands import EliminarUsuarioCommand
from servidor.logica.entities import Usuario
from servidor.logica.exceptions import UsuarioNoEncontrado
from servidor.logica.use_cases import EliminarUsuarioUseCase


def prueba_elimina_usuario_existente(repositorio):
    repositorio.insertar(Usuario("laura"))
    EliminarUsuarioUseCase(repositorio).ejecutar(EliminarUsuarioCommand(nick="laura"))
    assert repositorio.obtener_por_nick("laura") is None


def prueba_eliminar_inexistente_lanza_error(repositorio):
    with pytest.raises(UsuarioNoEncontrado):
        EliminarUsuarioUseCase(repositorio).ejecutar(EliminarUsuarioCommand(nick="nadie"))
