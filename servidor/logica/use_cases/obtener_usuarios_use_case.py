from servidor.datos.repositories.repositorio_usuarios import RepositorioUsuarios
from servidor.logica.entities.usuario import Usuario
from servidor.logica.queries.obtener_usuarios_query import ObtenerUsuariosQuery


class ObtenerUsuariosUseCase:
    def __init__(self, repositorio_usuarios: RepositorioUsuarios):
        self.repositorio_usuarios = repositorio_usuarios

    def ejecutar(self, query: ObtenerUsuariosQuery) -> list[Usuario]:
        return self.repositorio_usuarios.obtener_todos()
