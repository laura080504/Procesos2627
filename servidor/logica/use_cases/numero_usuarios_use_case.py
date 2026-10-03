from servidor.datos.repositories import RepositorioUsuarios
from servidor.logica.queries import NumeroUsuariosQuery


class NumeroUsuariosUseCase:
    def __init__(self, repositorio: RepositorioUsuarios):
        self.repositorio = repositorio

    def ejecutar(self, query: NumeroUsuariosQuery) -> int:
        return len(self.repositorio.obtener_todos())
