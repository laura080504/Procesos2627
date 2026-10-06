from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios
from Servidor.Dominio.DominioQueries.numero_usuarios_query import NumeroUsuariosQuery


class NumeroUsuariosUseCase:
    def __init__(self, repositorio_usuarios: RepositorioUsuarios):
        self.repositorio_usuarios = repositorio_usuarios

    def ejecutar(self, query: NumeroUsuariosQuery) -> int:
        return len(self.repositorio_usuarios.obtener_todos())
