from datetime import datetime, timezone

from servidor.infraestructura.repositories.repositorio_sesiones import RepositorioSesiones
from servidor.infraestructura.repositories.repositorio_usuarios import RepositorioUsuarios
from servidor.dominio.entities.usuario import Usuario
from servidor.dominio.exceptions.sesion_no_valida import SesionNoValida
from servidor.dominio.queries.obtener_usuario_sesion_query import ObtenerUsuarioSesionQuery


class ObtenerUsuarioSesionUseCase:
    def __init__(self, repositorio_sesiones: RepositorioSesiones, repositorio_usuarios: RepositorioUsuarios):
        self.repositorio_sesiones = repositorio_sesiones
        self.repositorio_usuarios = repositorio_usuarios

    def ejecutar(self, query: ObtenerUsuarioSesionQuery) -> Usuario:
        sesion = self.repositorio_sesiones.obtener(query.token)
        if sesion is None:
            raise SesionNoValida()
        if sesion.caducada(datetime.now(timezone.utc)):
            self.repositorio_sesiones.eliminar(sesion.token)
            raise SesionNoValida()

        usuario = self.repositorio_usuarios.obtener_por_email(sesion.email)
        if usuario is None:
            self.repositorio_sesiones.eliminar(sesion.token)
            raise SesionNoValida()
        return usuario
