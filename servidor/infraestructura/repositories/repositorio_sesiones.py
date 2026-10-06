from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from servidor.dominio.entities.sesion import Sesion


class RepositorioSesiones(ABC):
    @abstractmethod
    def guardar(self, sesion: Sesion) -> Sesion: ...

    @abstractmethod
    def obtener(self, token: str) -> Sesion | None: ...

    @abstractmethod
    def eliminar(self, token: str) -> None: ...

    @abstractmethod
    def eliminar_por_email(self, email: str) -> None: ...
