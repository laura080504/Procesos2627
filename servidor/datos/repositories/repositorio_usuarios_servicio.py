from __future__ import annotations

from typing import TYPE_CHECKING

from servidor.datos.repositories.repositorio_usuarios import RepositorioUsuarios

if TYPE_CHECKING:
    from servidor.logica.entities.usuario import Usuario


class RepositorioUsuariosServicio(RepositorioUsuarios):
    """BBDD externa (servicio en la nube). Pendiente de implementar en el hito 3."""

    def __init__(self, url_conexion: str):
        self.url_conexion = url_conexion

    def insertar(self, usuario: Usuario) -> Usuario:
        raise NotImplementedError

    def obtener_por_email(self, email: str) -> Usuario | None:
        raise NotImplementedError

    def obtener_todos(self) -> list[Usuario]:
        raise NotImplementedError

    def eliminar(self, email: str) -> bool:
        raise NotImplementedError
