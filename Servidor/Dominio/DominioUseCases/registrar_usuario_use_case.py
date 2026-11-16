from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas import RepositorioMatriculas
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios
from Servidor.Dominio.DominioCommands.registrar_usuario_command import RegistrarUsuarioCommand
from Servidor.Dominio.DominioEntities.usuario import Usuario
from Servidor.Dominio.DominioEnums.estado_usuario import EstadoUsuario
from Servidor.Dominio.DominioExceptions.usuario_ya_existe import UsuarioYaExiste
from Servidor.Dominio.DominioServices.hasher_contrasenas import HasherContrasenas
from Servidor.Dominio.DominioServices.matriculas_muestra import asegurar_matricula_de
from Servidor.Dominio.DominioUseCases.emitir_confirmacion_use_case import EmitirConfirmacionUseCase


class RegistrarUsuarioUseCase:
    def __init__(
        self,
        repositorio_usuarios: RepositorioUsuarios,
        hasher: HasherContrasenas,
        emitir_confirmacion: EmitirConfirmacionUseCase | None = None,
        repositorio_matriculas: RepositorioMatriculas | None = None,
    ):
        self.repositorio_usuarios = repositorio_usuarios
        self.hasher = hasher
        self.emitir_confirmacion = emitir_confirmacion
        self.repositorio_matriculas = repositorio_matriculas

    def ejecutar(self, command: RegistrarUsuarioCommand) -> Usuario:
        email = command.email.strip().lower()
        nick = command.nick.strip()
        if self.repositorio_usuarios.obtener_por_email(email):
            raise UsuarioYaExiste(email)
        self.repositorio_usuarios.insertar(
            Usuario(
                email=email,
                nick=nick,
                contrasena_hash=self.hasher.hashear(command.contrasena),
                estado=EstadoUsuario.PENDIENTE,
            )
        )
        guardado = self.repositorio_usuarios.obtener_por_email(email)
        if guardado is None:
            raise RuntimeError(f"No se ha podido guardar el usuario {email}")
        if self.emitir_confirmacion is not None:
            try:
                self.emitir_confirmacion.ejecutar(email, command.url_base)
            except Exception:
                self.repositorio_usuarios.eliminar(email)
                raise
            guardado = self.repositorio_usuarios.obtener_por_email(email)
        if self.repositorio_matriculas is not None and guardado is not None:
            asegurar_matricula_de(self.repositorio_matriculas, guardado.email)
        return guardado
