from servidor.infraestructura.repositories.repositorio_usuarios import RepositorioUsuarios
from servidor.dominio.entities.usuario import Usuario
from servidor.dominio.enums.rol import Rol
from servidor.dominio.services.hasher_contrasenas import HasherContrasenas


class AsegurarAdministradorUseCase:
    def __init__(self, repositorio_usuarios: RepositorioUsuarios, hasher: HasherContrasenas):
        self.repositorio_usuarios = repositorio_usuarios
        self.hasher = hasher

    def ejecutar(self, email: str, contrasena: str) -> None:
        if any(usuario.rol == Rol.ADMINISTRADOR for usuario in self.repositorio_usuarios.obtener_todos()):
            return
        email = email.strip().lower()
        existente = self.repositorio_usuarios.obtener_por_email(email)
        if existente is None:
            self.repositorio_usuarios.insertar(
                Usuario(
                    email=email,
                    nick=email.split("@")[0][:30],
                    contrasena_hash=self.hasher.hashear(contrasena),
                    rol=Rol.ADMINISTRADOR,
                )
            )
            return
        existente.rol = Rol.ADMINISTRADOR
        self.repositorio_usuarios.actualizar(existente)
