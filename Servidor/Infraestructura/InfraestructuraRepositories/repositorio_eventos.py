from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Servidor.Dominio.DominioEntities.evento import Evento


class RepositorioEventos(ABC):
    @abstractmethod
    def obtener_todos(self) -> list[Evento]: ...

    @abstractmethod
    def reemplazar(self, eventos: list[Evento]) -> None: ...
