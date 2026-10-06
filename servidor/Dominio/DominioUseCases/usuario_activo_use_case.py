from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios
from Servidor.Dominio.DominioEnums.estado_usuario import EstadoUsuario
from Servidor.Dominio.DominioQueries.usuario_activo_query import UsuarioActivoQuery


class UsuarioActivoUseCase:
    def __init__(self, repositorio_usuarios: RepositorioUsuarios):
        self.repositorio_usuarios = repositorio_usuarios

    def ejecutar(self, query: UsuarioActivoQuery) -> bool:
        usuario = self.repositorio_usuarios.obtener_por_email(query.email.strip().lower())
        return usuario is not None and usuario.estado == EstadoUsuario.ACTIVO
