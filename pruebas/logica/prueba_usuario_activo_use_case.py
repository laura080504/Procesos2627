from servidor.logica.entities import Usuario
from servidor.logica.enums import EstadoUsuario
from servidor.logica.queries import UsuarioActivoQuery
from servidor.logica.use_cases import UsuarioActivoUseCase


def prueba_usuario_existente_esta_activo(repositorio):
    repositorio.insertar(Usuario("laura"))
    assert UsuarioActivoUseCase(repositorio).ejecutar(UsuarioActivoQuery(nick="laura"))


def prueba_usuario_inexistente_no_esta_activo(repositorio):
    assert not UsuarioActivoUseCase(repositorio).ejecutar(UsuarioActivoQuery(nick="nadie"))


def prueba_usuario_pendiente_no_esta_activo(repositorio):
    repositorio.insertar(Usuario("laura", estado=EstadoUsuario.PENDIENTE))
    assert not UsuarioActivoUseCase(repositorio).ejecutar(UsuarioActivoQuery(nick="laura"))
