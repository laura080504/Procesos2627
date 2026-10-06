from servidor.dominio.queries.obtener_usuarios_query import ObtenerUsuariosQuery
from servidor.dominio.use_cases.obtener_usuarios_use_case import ObtenerUsuariosUseCase


def prueba_inicialmente_no_hay_usuarios(repositorio_usuarios):
    assert ObtenerUsuariosUseCase(repositorio_usuarios).ejecutar(ObtenerUsuariosQuery()) == []


def prueba_devuelve_los_usuarios_guardados(repositorio_usuarios, usuario_registrado):
    usuarios = ObtenerUsuariosUseCase(repositorio_usuarios).ejecutar(ObtenerUsuariosQuery())
    assert usuarios == [usuario_registrado]
