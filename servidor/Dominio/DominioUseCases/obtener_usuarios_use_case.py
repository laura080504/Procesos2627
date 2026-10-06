from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios
from Servidor.Dominio.DominioEntities.usuario import Usuario
from Servidor.Dominio.DominioQueries.obtener_usuarios_query import ObtenerUsuariosQuery


class ObtenerUsuariosUseCase:
    def __init__(self, repositorio_usuarios: RepositorioUsuarios):
        self.repositorio_usuarios = repositorio_usuarios

    def ejecutar(self, query: ObtenerUsuariosQuery) -> list[Usuario]:
        return self.repositorio_usuarios.obtener_todos()
