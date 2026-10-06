import secrets
from datetime import datetime, timedelta, timezone

from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_sesiones import RepositorioSesiones
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios
from Servidor.Dominio.DominioCommands.iniciar_sesion_command import IniciarSesionCommand
from Servidor.Dominio.DominioEntities.sesion import Sesion
from Servidor.Dominio.DominioEnums.estado_usuario import EstadoUsuario
from Servidor.Dominio.DominioExceptions.credenciales_invalidas import CredencialesInvalidas
from Servidor.Dominio.DominioExceptions.cuenta_pendiente import CuentaPendiente
from Servidor.Dominio.DominioResults.inicio_sesion_resultado import InicioSesionResultado
from Servidor.Dominio.DominioServices.hasher_contrasenas import HasherContrasenas


class IniciarSesionUseCase:
    def __init__(
        self,
        repositorio_usuarios: RepositorioUsuarios,
        repositorio_sesiones: RepositorioSesiones,
        hasher: HasherContrasenas,
        duracion_sesion: timedelta,
    ):
        self.repositorio_usuarios = repositorio_usuarios
        self.repositorio_sesiones = repositorio_sesiones
        self.hasher = hasher
        self.duracion_sesion = duracion_sesion

    def ejecutar(self, command: IniciarSesionCommand) -> InicioSesionResultado:
        email = command.email.strip().lower()
        usuario = self.repositorio_usuarios.obtener_por_email(email)
        if usuario is None or not self.hasher.verificar(command.contrasena, usuario.contrasena_hash):
            raise CredencialesInvalidas()
        if usuario.estado == EstadoUsuario.PENDIENTE:
            raise CuentaPendiente(email)

        sesion = Sesion(
            token=secrets.token_urlsafe(32),
            email=email,
            expira_en=datetime.now(timezone.utc) + self.duracion_sesion,
        )
        self.repositorio_sesiones.guardar(sesion)
        return InicioSesionResultado(sesion=sesion, usuario=usuario)
