from __future__ import annotations

from typing import TYPE_CHECKING

from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios

if TYPE_CHECKING:
    from Servidor.Dominio.DominioEntities.usuario import Usuario


class RepositorioUsuariosMemoria(RepositorioUsuarios):
    def __init__(self):
        self._usuarios: dict[str, Usuario] = {}

    def insertar(self, usuario: Usuario) -> Usuario:
        self._usuarios[usuario.email] = usuario
        return usuario

    def obtener_por_email(self, email: str) -> Usuario | None:
        return self._usuarios.get(email)

    def obtener_todos(self) -> list[Usuario]:
        return list(self._usuarios.values())

    def actualizar(self, usuario: Usuario) -> None:
        if usuario.email in self._usuarios:
            self._usuarios[usuario.email] = usuario

    def eliminar(self, email: str) -> bool:
        return self._usuarios.pop(email, None) is not None
