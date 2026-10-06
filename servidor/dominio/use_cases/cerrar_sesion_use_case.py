from servidor.infraestructura.repositories.repositorio_sesiones import RepositorioSesiones
from servidor.dominio.commands.cerrar_sesion_command import CerrarSesionCommand


class CerrarSesionUseCase:
    def __init__(self, repositorio_sesiones: RepositorioSesiones):
        self.repositorio_sesiones = repositorio_sesiones

    def ejecutar(self, command: CerrarSesionCommand) -> None:
        self.repositorio_sesiones.eliminar(command.token)
