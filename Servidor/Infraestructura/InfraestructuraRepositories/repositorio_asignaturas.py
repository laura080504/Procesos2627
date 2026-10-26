from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Servidor.Dominio.DominioEntities.asignatura import Asignatura


class RepositorioAsignaturas(ABC):
    @abstractmethod
    def obtener_todas(self) -> list[Asignatura]: ...

    @abstractmethod
    def reemplazar(self, asignaturas: list[Asignatura]) -> None: ...
