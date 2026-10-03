from servidor.logica.entities import Usuario
from servidor.logica.queries import ObtenerUsuariosQuery
from servidor.logica.use_cases import ObtenerUsuariosUseCase


def prueba_inicialmente_no_hay_usuarios(repositorio):
    assert ObtenerUsuariosUseCase(repositorio).ejecutar(ObtenerUsuariosQuery()) == []


def prueba_devuelve_los_usuarios_guardados(repositorio):
    repositorio.insertar(Usuario("laura"))
    repositorio.insertar(Usuario("pepe"))
    usuarios = ObtenerUsuariosUseCase(repositorio).ejecutar(ObtenerUsuariosQuery())
    assert [usuario.nick for usuario in usuarios] == ["laura", "pepe"]
