from servidor.logica.entities import Usuario
from servidor.logica.queries import NumeroUsuariosQuery
from servidor.logica.use_cases import NumeroUsuariosUseCase


def prueba_cuenta_los_usuarios(repositorio):
    use_case = NumeroUsuariosUseCase(repositorio)
    assert use_case.ejecutar(NumeroUsuariosQuery()) == 0
    repositorio.insertar(Usuario("laura"))
    assert use_case.ejecutar(NumeroUsuariosQuery()) == 1
