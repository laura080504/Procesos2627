from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios
from Servidor.Dominio.DominioEntities.usuario import Usuario
from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Dominio.DominioServices.hasher_contrasenas import HasherContrasenas


class AsegurarSecretariaUseCase:
    """Crea o promociona la cuenta de secretaría (único superadministrador de arranque)."""

    def __init__(self, repositorio_usuarios: RepositorioUsuarios, hasher: HasherContrasenas):
        self.repositorio_usuarios = repositorio_usuarios
        self.hasher = hasher

    def ejecutar(self, email: str, contrasena: str) -> None:
        email = email.strip().lower()
        usuarios = self.repositorio_usuarios.obtener_todos()
        if any(usuario.rol == Rol.SUPERADMINISTRADOR and usuario.email != email for usuario in usuarios):
            return
        existente = self.repositorio_usuarios.obtener_por_email(email)
        if existente is None:
            self.repositorio_usuarios.insertar(
                Usuario(
                    email=email,
                    nick=email.split("@")[0][:30],
                    contrasena_hash=self.hasher.hashear(contrasena),
                    rol=Rol.SUPERADMINISTRADOR,
                )
            )
            return
        if existente.rol != Rol.SUPERADMINISTRADOR:
            existente.rol = Rol.SUPERADMINISTRADOR
            self.repositorio_usuarios.actualizar(existente)
