from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_recuperaciones import RepositorioRecuperaciones
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_sesiones import RepositorioSesiones
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios
from Servidor.Dominio.DominioCommands.eliminar_usuario_command import EliminarUsuarioCommand
from Servidor.Dominio.DominioEnums.estado_usuario import EstadoUsuario
from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Dominio.DominioExceptions.permiso_insuficiente import PermisoInsuficiente
from Servidor.Dominio.DominioExceptions.usuario_no_encontrado import UsuarioNoEncontrado


class EliminarUsuarioUseCase:
    def __init__(
        self,
        repositorio_usuarios: RepositorioUsuarios,
        repositorio_sesiones: RepositorioSesiones,
        repositorio_recuperaciones: RepositorioRecuperaciones,
    ):
        self.repositorio_usuarios = repositorio_usuarios
        self.repositorio_sesiones = repositorio_sesiones
        self.repositorio_recuperaciones = repositorio_recuperaciones

    def ejecutar(self, command: EliminarUsuarioCommand) -> None:
        email = command.email.strip().lower()
        solicitante = command.solicitante_email.strip().lower()
        if command.solicitante_rol != Rol.ADMINISTRADOR and solicitante != email:
            raise PermisoInsuficiente()
        usuario = self.repositorio_usuarios.obtener_por_email(email)
        if usuario is None or usuario.estado == EstadoUsuario.ELIMINADO:
            raise UsuarioNoEncontrado(email)
        usuario.estado = EstadoUsuario.ELIMINADO
        self.repositorio_usuarios.actualizar(usuario)
        self.repositorio_sesiones.eliminar_por_email(email)
        self.repositorio_recuperaciones.eliminar_por_email(email)
