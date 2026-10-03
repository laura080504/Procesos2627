from __future__ import annotations

from typing import TYPE_CHECKING

from servidor.datos.repositories.repositorio_usuarios import RepositorioUsuarios

if TYPE_CHECKING:
    from servidor.logica.entities import Usuario


class RepositorioUsuariosMemoria(RepositorioUsuarios):
    """BBDD local del servidor (en memoria)."""

    def __init__(self):
        self._usuarios: dict[str, Usuario] = {}

    def insertar(self, usuario: Usuario) -> Usuario:
        self._usuarios[usuario.nick] = usuario
        return usuario

    def obtener_por_nick(self, nick: str) -> Usuario | None:
        return self._usuarios.get(nick)

    def obtener_todos(self) -> list[Usuario]:
        return list(self._usuarios.values())

    def eliminar(self, nick: str) -> bool:
        return self._usuarios.pop(nick, None) is not None
