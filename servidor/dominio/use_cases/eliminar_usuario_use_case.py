from servidor.infraestructura.repositories.repositorio_sesiones import RepositorioSesiones
from servidor.infraestructura.repositories.repositorio_usuarios import RepositorioUsuarios
from servidor.dominio.commands.eliminar_usuario_command import EliminarUsuarioCommand
from servidor.dominio.enums.rol import Rol
from servidor.dominio.exceptions.permiso_insuficiente import PermisoInsuficiente
from servidor.dominio.exceptions.usuario_no_encontrado import UsuarioNoEncontrado


class EliminarUsuarioUseCase:
    def __init__(self, repositorio_usuarios: RepositorioUsuarios, repositorio_sesiones: RepositorioSesiones):
        self.repositorio_usuarios = repositorio_usuarios
        self.repositorio_sesiones = repositorio_sesiones

    def ejecutar(self, command: EliminarUsuarioCommand) -> None:
        email = command.email.strip().lower()
        solicitante = command.solicitante_email.strip().lower()
        if command.solicitante_rol != Rol.ADMINISTRADOR and solicitante != email:
            raise PermisoInsuficiente()
        if not self.repositorio_usuarios.eliminar(email):
            raise UsuarioNoEncontrado(email)
        self.repositorio_sesiones.eliminar_por_email(email)
