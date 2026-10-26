from __future__ import annotations

from abc import ABC, abstractmethod


class RepositorioMatriculas(ABC):
    @abstractmethod
    def obtener_codigos(self, email: str) -> list[str]: ...

    @abstractmethod
    def obtener_notas(self, email: str) -> dict[str, float | None]: ...

    @abstractmethod
    def reemplazar_alumno(self, email: str, codigos: list[str]) -> None: ...

    @abstractmethod
    def rellenar_notas(self, email: str, notas: dict[str, float]) -> None: ...
