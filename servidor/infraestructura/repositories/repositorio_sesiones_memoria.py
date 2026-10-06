from __future__ import annotations

from typing import TYPE_CHECKING

from servidor.infraestructura.repositories.repositorio_sesiones import RepositorioSesiones

if TYPE_CHECKING:
    from servidor.dominio.entities.sesion import Sesion


class RepositorioSesionesMemoria(RepositorioSesiones):
    def __init__(self):
        self._sesiones: dict[str, Sesion] = {}

    def guardar(self, sesion: Sesion) -> Sesion:
        self._sesiones[sesion.token] = sesion
        return sesion

    def obtener(self, token: str) -> Sesion | None:
        return self._sesiones.get(token)

    def eliminar(self, token: str) -> None:
        self._sesiones.pop(token, None)

    def eliminar_por_email(self, email: str) -> None:
        for token in [t for t, s in self._sesiones.items() if s.email == email]:
            del self._sesiones[token]
