from datetime import datetime, timedelta, timezone

from Servidor.Dominio.DominioCommands.iniciar_sesion_command import IniciarSesionCommand
from Servidor.Dominio.DominioEntities.sesion import Sesion
from Servidor.Dominio.DominioEnums.estado_usuario import EstadoUsuario
from Servidor.Dominio.DominioExceptions.credenciales_invalidas import CredencialesInvalidas
from Servidor.Dominio.DominioExceptions.cuenta_eliminada import CuentaEliminada
from Servidor.Dominio.DominioExceptions.cuenta_pendiente import CuentaPendiente
from Servidor.Dominio.DominioResults.inicio_sesion_resultado import InicioSesionResultado
from Servidor.Dominio.DominioServices.hasher_contrasenas import HasherContrasenas
from Servidor.Dominio.DominioServices.matriculas_muestra import asegurar_matricula_de
from Servidor.Dominio.DominioServices.token_seguro import nuevo_token
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas import RepositorioMatriculas
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_sesiones import RepositorioSesiones
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios

# Hash bcrypt fijo (coste 12) para igualar tiempos cuando el email no existe.
_HASH_CEBO = "$2b$12$NaYR31lrq2IXxQN.1CzXZOlH.8JVQQphBehgAoYqW4LcGwLevLRg2"


class IniciarSesionUseCase:
    def __init__(
        self,
        repositorio_usuarios: RepositorioUsuarios,
        repositorio_sesiones: RepositorioSesiones,
        hasher: HasherContrasenas,
        duracion_sesion: timedelta,
        repositorio_matriculas: RepositorioMatriculas | None = None,
        duracion_sesion_corta: timedelta | None = None,
        duracion_sesion_larga: timedelta | None = None,
    ):
        self.repositorio_usuarios = repositorio_usuarios
        self.repositorio_sesiones = repositorio_sesiones
        self.hasher = hasher
        self.duracion_sesion = duracion_sesion
        self.repositorio_matriculas = repositorio_matriculas
        self.duracion_sesion_corta = duracion_sesion_corta or timedelta(hours=2)
        self.duracion_sesion_larga = duracion_sesion_larga or timedelta(days=30)

    def ejecutar(self, command: IniciarSesionCommand) -> InicioSesionResultado:
        email = command.email.strip().lower()
        usuario = self.repositorio_usuarios.obtener_por_email(email)
        if usuario is None or not usuario.contrasena_hash:
            self.hasher.verificar(command.contrasena, _HASH_CEBO)
            raise CredencialesInvalidas()
        if usuario.estado == EstadoUsuario.ELIMINADO:
            raise CuentaEliminada(email)
        if not self.hasher.verificar(command.contrasena, usuario.contrasena_hash):
            raise CredencialesInvalidas()
        if usuario.estado == EstadoUsuario.PENDIENTE:
            raise CuentaPendiente(email)

        if self.repositorio_matriculas is not None:
            asegurar_matricula_de(self.repositorio_matriculas, email)

        duracion = self.duracion_sesion_larga if command.recordar else self.duracion_sesion_corta
        sesion = Sesion(
            token=nuevo_token(),
            email=email,
            expira_en=datetime.now(timezone.utc) + duracion,
        )
        self.repositorio_sesiones.guardar(sesion)
        return InicioSesionResultado(sesion=sesion, usuario=usuario)
