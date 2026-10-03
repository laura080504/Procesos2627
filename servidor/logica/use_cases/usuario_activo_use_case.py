from servidor.datos.repositories import RepositorioUsuarios
from servidor.logica.enums import EstadoUsuario
from servidor.logica.queries import UsuarioActivoQuery


class UsuarioActivoUseCase:
    def __init__(self, repositorio: RepositorioUsuarios):
        self.repositorio = repositorio

    def ejecutar(self, query: UsuarioActivoQuery) -> bool:
        usuario = self.repositorio.obtener_por_nick(query.nick)
        return usuario is not None and usuario.estado == EstadoUsuario.ACTIVO
