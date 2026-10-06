from datetime import datetime, timezone

from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_recuperaciones import RepositorioRecuperaciones
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_sesiones import RepositorioSesiones
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios
from Servidor.Dominio.DominioCommands.restablecer_contrasena_command import RestablecerContrasenaCommand
from Servidor.Dominio.DominioExceptions.recuperacion_no_valida import RecuperacionNoValida
from Servidor.Dominio.DominioServices.hasher_contrasenas import HasherContrasenas


class RestablecerContrasenaUseCase:
    def __init__(
        self,
        repositorio_usuarios: RepositorioUsuarios,
        repositorio_recuperaciones: RepositorioRecuperaciones,
        repositorio_sesiones: RepositorioSesiones,
        hasher: HasherContrasenas,
    ):
        self.repositorio_usuarios = repositorio_usuarios
        self.repositorio_recuperaciones = repositorio_recuperaciones
        self.repositorio_sesiones = repositorio_sesiones
        self.hasher = hasher

    def ejecutar(self, command: RestablecerContrasenaCommand) -> None:
        recuperacion = self.repositorio_recuperaciones.obtener(command.token)
        if recuperacion is None or recuperacion.caducada(datetime.now(timezone.utc)):
            if recuperacion is not None:
                self.repositorio_recuperaciones.eliminar(recuperacion.token)
            raise RecuperacionNoValida()

        usuario = self.repositorio_usuarios.obtener_por_email(recuperacion.email)
        if usuario is None:
            self.repositorio_recuperaciones.eliminar(recuperacion.token)
            raise RecuperacionNoValida()

        usuario.contrasena_hash = self.hasher.hashear(command.contrasena)
        self.repositorio_usuarios.actualizar(usuario)
        self.repositorio_recuperaciones.eliminar(recuperacion.token)
        self.repositorio_sesiones.eliminar_por_email(recuperacion.email)
