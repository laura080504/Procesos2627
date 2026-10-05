from __future__ import annotations

from typing import TYPE_CHECKING

from servidor.datos.repositories.repositorio_usuarios import RepositorioUsuarios

if TYPE_CHECKING:
    from servidor.logica.entities.usuario import Usuario


class RepositorioUsuariosMemoria(RepositorioUsuarios):
    """BBDD local del servidor (en memoria)."""

    def __init__(self):
        self._usuarios: dict[str, Usuario] = {}

    def insertar(self, usuario: Usuario) -> Usuario:
        self._usuarios[usuario.email] = usuario
        return usuario

    def obtener_por_email(self, email: str) -> Usuario | None:
        return self._usuarios.get(email)

    def obtener_todos(self) -> list[Usuario]:
        return list(self._usuarios.values())

    def eliminar(self, email: str) -> bool:
        return self._usuarios.pop(email, None) is not None
