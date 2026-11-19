from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios
from Servidor.Dominio.DominioEntities.usuario import Usuario
from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Dominio.DominioServices.hasher_contrasenas import HasherContrasenas


class AsegurarAdministradorUseCase:
    """Asegura la cuenta de administrador (= profesor), no de secretaría.

    El superadministrador es solo secretaría; se crea aparte con
    ``AsegurarSecretariaUseCase``.
    """

    def __init__(self, repositorio_usuarios: RepositorioUsuarios, hasher: HasherContrasenas):
        self.repositorio_usuarios = repositorio_usuarios
        self.hasher = hasher

    def ejecutar(self, email: str, contrasena: str) -> None:
        email = email.strip().lower()
        existente = self.repositorio_usuarios.obtener_por_email(email)
        if existente is None:
            self.repositorio_usuarios.insertar(
                Usuario(
                    email=email,
                    nick=email.split("@")[0][:30],
                    contrasena_hash=self.hasher.hashear(contrasena),
                    rol=Rol.PROFESOR,
                )
            )
            return
        if existente.rol != Rol.PROFESOR:
            existente.rol = Rol.PROFESOR
            self.repositorio_usuarios.actualizar(existente)
