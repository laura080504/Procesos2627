from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios
from Servidor.Dominio.DominioCommands.asignar_administrador_command import AsignarAdministradorCommand
from Servidor.Dominio.DominioEntities.usuario import Usuario
from Servidor.Dominio.DominioEnums.estado_usuario import EstadoUsuario
from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Dominio.DominioExceptions.permiso_insuficiente import PermisoInsuficiente
from Servidor.Dominio.DominioExceptions.usuario_no_encontrado import UsuarioNoEncontrado


class AsignarAdministradorUseCase:
    def __init__(self, repositorio_usuarios: RepositorioUsuarios):
        self.repositorio_usuarios = repositorio_usuarios

    def ejecutar(self, command: AsignarAdministradorCommand) -> Usuario:
        if command.solicitante_rol != Rol.SUPERADMINISTRADOR:
            raise PermisoInsuficiente()
        email = command.email.strip().lower()
        usuario = self.repositorio_usuarios.obtener_por_email(email)
        if usuario is None or usuario.estado == EstadoUsuario.ELIMINADO:
            raise UsuarioNoEncontrado(email)
        if usuario.rol == Rol.SUPERADMINISTRADOR:
            raise PermisoInsuficiente()
        usuario.rol = Rol.PROFESOR
        self.repositorio_usuarios.actualizar(usuario)
        guardado = self.repositorio_usuarios.obtener_por_email(email)
        if guardado is None:
            raise RuntimeError(f"No se ha podido actualizar el rol de {email}")
        return guardado
