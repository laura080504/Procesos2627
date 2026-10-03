from servidor.datos.repositories import RepositorioUsuarios
from servidor.logica.commands import AgregarUsuarioCommand
from servidor.logica.entities import Usuario
from servidor.logica.exceptions import UsuarioYaExiste


class AgregarUsuarioUseCase:
    def __init__(self, repositorio: RepositorioUsuarios):
        self.repositorio = repositorio

    def ejecutar(self, command: AgregarUsuarioCommand) -> Usuario:
        nick = command.nick.strip()
        if self.repositorio.obtener_por_nick(nick):
            raise UsuarioYaExiste(nick)
        return self.repositorio.insertar(Usuario(nick))
