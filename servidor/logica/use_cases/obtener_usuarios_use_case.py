from servidor.datos.repositories import RepositorioUsuarios
from servidor.logica.entities import Usuario
from servidor.logica.queries import ObtenerUsuariosQuery


class ObtenerUsuariosUseCase:
    def __init__(self, repositorio: RepositorioUsuarios):
        self.repositorio = repositorio

    def ejecutar(self, query: ObtenerUsuariosQuery) -> list[Usuario]:
        return self.repositorio.obtener_todos()
