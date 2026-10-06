import secrets
from datetime import datetime, timedelta, timezone

from servidor.infraestructura.repositories.repositorio_recuperaciones import RepositorioRecuperaciones
from servidor.infraestructura.repositories.repositorio_usuarios import RepositorioUsuarios
from servidor.dominio.commands.solicitar_recuperacion_command import SolicitarRecuperacionCommand
from servidor.dominio.entities.recuperacion import Recuperacion
from servidor.dominio.exceptions.usuario_no_encontrado import UsuarioNoEncontrado


class SolicitarRecuperacionUseCase:
    def __init__(
        self,
        repositorio_usuarios: RepositorioUsuarios,
        repositorio_recuperaciones: RepositorioRecuperaciones,
        duracion: timedelta,
    ):
        self.repositorio_usuarios = repositorio_usuarios
        self.repositorio_recuperaciones = repositorio_recuperaciones
        self.duracion = duracion

    def ejecutar(self, command: SolicitarRecuperacionCommand) -> Recuperacion:
        email = command.email.strip().lower()
        if self.repositorio_usuarios.obtener_por_email(email) is None:
            raise UsuarioNoEncontrado(email)
        self.repositorio_recuperaciones.eliminar_por_email(email)
        recuperacion = Recuperacion(
            token=secrets.token_urlsafe(32),
            email=email,
            expira_en=datetime.now(timezone.utc) + self.duracion,
        )
        return self.repositorio_recuperaciones.guardar(recuperacion)
