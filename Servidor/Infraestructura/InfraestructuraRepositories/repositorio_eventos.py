from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Servidor.Dominio.DominioEntities.evento import Evento


class RepositorioEventos(ABC):
    @abstractmethod
    def obtener_todos(self) -> list[Evento]: ...

    @abstractmethod
    def obtener_por_id(self, evento_id: str) -> Evento | None: ...

    @abstractmethod
    def reemplazar(self, eventos: list[Evento]) -> None: ...

    @abstractmethod
    def guardar(self, evento: Evento) -> None: ...

    @abstractmethod
    def eliminar(self, evento_id: str) -> bool: ...
