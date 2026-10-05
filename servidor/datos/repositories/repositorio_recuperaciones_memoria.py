from __future__ import annotations

from typing import TYPE_CHECKING

from servidor.datos.repositories.repositorio_recuperaciones import RepositorioRecuperaciones

if TYPE_CHECKING:
    from servidor.logica.entities.recuperacion import Recuperacion


class RepositorioRecuperacionesMemoria(RepositorioRecuperaciones):
    def __init__(self):
        self._recuperaciones: dict[str, Recuperacion] = {}

    def guardar(self, recuperacion: Recuperacion) -> Recuperacion:
        self._recuperaciones[recuperacion.token] = recuperacion
        return recuperacion

    def obtener(self, token: str) -> Recuperacion | None:
        return self._recuperaciones.get(token)

    def eliminar(self, token: str) -> None:
        self._recuperaciones.pop(token, None)

    def eliminar_por_email(self, email: str) -> None:
        for token in [t for t, r in self._recuperaciones.items() if r.email == email]:
            del self._recuperaciones[token]
