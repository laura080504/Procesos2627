from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_recuperaciones import RepositorioRecuperaciones
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_sesiones import RepositorioSesiones
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios
from Servidor.Dominio.DominioCommands.editar_datos_command import EditarDatosCommand
from Servidor.Dominio.DominioEntities.usuario import Usuario
from Servidor.Dominio.DominioEnums.estado_usuario import EstadoUsuario
from Servidor.Dominio.DominioExceptions.usuario_no_encontrado import UsuarioNoEncontrado
from Servidor.Dominio.DominioExceptions.usuario_ya_existe import UsuarioYaExiste
from Servidor.Dominio.DominioServices.hasher_contrasenas import HasherContrasenas


class EditarDatosUseCase:
    def __init__(
        self,
        repositorio_usuarios: RepositorioUsuarios,
        repositorio_sesiones: RepositorioSesiones,
        repositorio_recuperaciones: RepositorioRecuperaciones,
        hasher: HasherContrasenas,
    ):
        self.repositorio_usuarios = repositorio_usuarios
        self.repositorio_sesiones = repositorio_sesiones
        self.repositorio_recuperaciones = repositorio_recuperaciones
        self.hasher = hasher

    def ejecutar(self, command: EditarDatosCommand) -> Usuario:
        email_actual = command.solicitante_email.strip().lower()
        email_nuevo = command.email.strip().lower()
        nick = command.nick.strip()
        usuario = self.repositorio_usuarios.obtener_por_email(email_actual)
        if usuario is None or usuario.estado == EstadoUsuario.ELIMINADO:
            raise UsuarioNoEncontrado(email_actual)
        if email_nuevo != email_actual:
            ocupado = self.repositorio_usuarios.obtener_por_email(email_nuevo)
            if ocupado is not None:
                raise UsuarioYaExiste(email_nuevo)
        usuario.nick = nick
        if command.contrasena:
            usuario.contrasena_hash = self.hasher.hashear(command.contrasena)
        if email_nuevo != email_actual:
            usuario.email = email_nuevo
            self.repositorio_usuarios.cambiar_email(email_actual, usuario)
            self.repositorio_sesiones.actualizar_email(email_actual, email_nuevo)
            self.repositorio_recuperaciones.actualizar_email(email_actual, email_nuevo)
        else:
            self.repositorio_usuarios.actualizar(usuario)
        guardado = self.repositorio_usuarios.obtener_por_email(email_nuevo)
        if guardado is None:
            raise RuntimeError(f"No se han podido guardar los datos de {email_nuevo}")
        return guardado
