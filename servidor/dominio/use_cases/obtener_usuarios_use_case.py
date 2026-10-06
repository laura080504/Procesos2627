from servidor.infraestructura.repositories.repositorio_usuarios import RepositorioUsuarios
from servidor.dominio.entities.usuario import Usuario
from servidor.dominio.queries.obtener_usuarios_query import ObtenerUsuariosQuery


class ObtenerUsuariosUseCase:
    def __init__(self, repositorio_usuarios: RepositorioUsuarios):
        self.repositorio_usuarios = repositorio_usuarios

    def ejecutar(self, query: ObtenerUsuariosQuery) -> list[Usuario]:
        return self.repositorio_usuarios.obtener_todos()
