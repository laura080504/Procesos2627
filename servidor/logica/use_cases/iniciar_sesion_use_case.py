import secrets
from datetime import datetime, timedelta, timezone

from servidor.datos.repositories.repositorio_sesiones import RepositorioSesiones
from servidor.datos.repositories.repositorio_usuarios import RepositorioUsuarios
from servidor.logica.commands.iniciar_sesion_command import IniciarSesionCommand
from servidor.logica.entities.sesion import Sesion
from servidor.logica.enums.estado_usuario import EstadoUsuario
from servidor.logica.exceptions.credenciales_invalidas import CredencialesInvalidas
from servidor.logica.exceptions.cuenta_pendiente import CuentaPendiente
from servidor.logica.results.inicio_sesion_resultado import InicioSesionResultado
from servidor.logica.services.hasher_contrasenas import HasherContrasenas


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
