from servidor.datos.repositories import RepositorioUsuarios
from servidor.logica.commands import EliminarUsuarioCommand
from servidor.logica.exceptions import UsuarioNoEncontrado


class EliminarUsuarioUseCase:
    def __init__(self, repositorio: RepositorioUsuarios):
        self.repositorio = repositorio

    def ejecutar(self, command: EliminarUsuarioCommand) -> None:
        if not self.repositorio.eliminar(command.nick):
            raise UsuarioNoEncontrado(command.nick)
