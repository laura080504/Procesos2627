from servidor.datos.repositories.repositorio_usuarios import RepositorioUsuarios
from servidor.logica.commands.registrar_usuario_command import RegistrarUsuarioCommand
from servidor.logica.entities.usuario import Usuario
from servidor.logica.exceptions.usuario_ya_existe import UsuarioYaExiste
from servidor.logica.services.hasher_contrasenas import HasherContrasenas


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
