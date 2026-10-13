from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios
from Servidor.Dominio.DominioCommands.registrar_usuario_command import RegistrarUsuarioCommand
from Servidor.Dominio.DominioEntities.usuario import Usuario
from Servidor.Dominio.DominioExceptions.usuario_ya_existe import UsuarioYaExiste
from Servidor.Dominio.DominioServices.hasher_contrasenas import HasherContrasenas


class RegistrarUsuarioUseCase:
    def __init__(self, repositorio_usuarios: RepositorioUsuarios, hasher: HasherContrasenas):
        self.repositorio_usuarios = repositorio_usuarios
        self.hasher = hasher

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
            )
        )
        guardado = self.repositorio_usuarios.obtener_por_email(email)
        if guardado is None:
            raise RuntimeError(f"No se ha podido guardar el usuario {email}")
        return guardado
