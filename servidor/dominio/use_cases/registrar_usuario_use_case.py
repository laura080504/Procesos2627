from servidor.infraestructura.repositories.repositorio_usuarios import RepositorioUsuarios
from servidor.dominio.commands.registrar_usuario_command import RegistrarUsuarioCommand
from servidor.dominio.entities.usuario import Usuario
from servidor.dominio.exceptions.usuario_ya_existe import UsuarioYaExiste
from servidor.dominio.services.hasher_contrasenas import HasherContrasenas


class RegistrarUsuarioUseCase:
    def __init__(self, repositorio_usuarios: RepositorioUsuarios, hasher: HasherContrasenas):
        self.repositorio_usuarios = repositorio_usuarios
        self.hasher = hasher

    def ejecutar(self, command: RegistrarUsuarioCommand) -> Usuario:
        email = command.email.strip().lower()
        if self.repositorio_usuarios.obtener_por_email(email):
            raise UsuarioYaExiste(email)
        usuario = Usuario(
            email=email,
            nick=command.nick.strip(),
            contrasena_hash=self.hasher.hashear(command.contrasena),
        )
        return self.repositorio_usuarios.insertar(usuario)
