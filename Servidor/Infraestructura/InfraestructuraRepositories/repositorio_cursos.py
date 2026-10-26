from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Servidor.Dominio.DominioEntities.asignatura import Asignatura


class RepositorioCursos(ABC):
    @abstractmethod
    def obtener(self, curso: str) -> list[Asignatura]: ...

    @abstractmethod
    def guardar(self, asignatura: Asignatura) -> None: ...
