from Servidor.Dominio.DominioQueries.numero_usuarios_query import NumeroUsuariosQuery
from Servidor.Dominio.DominioUseCases.numero_usuarios_use_case import NumeroUsuariosUseCase


def prueba_sin_usuarios_devuelve_cero(repositorio_usuarios):
    assert NumeroUsuariosUseCase(repositorio_usuarios).ejecutar(NumeroUsuariosQuery()) == 0


def prueba_cuenta_los_usuarios(repositorio_usuarios, usuario_registrado):
    assert NumeroUsuariosUseCase(repositorio_usuarios).ejecutar(NumeroUsuariosQuery()) == 1
