from __future__ import annotations

from abc import ABC, abstractmethod


class RepositorioMatriculas(ABC):
    @abstractmethod
    def obtener_codigos(self, email: str) -> list[str]: ...

    @abstractmethod
    def obtener_notas(self, email: str) -> dict[str, float | None]: ...

    @abstractmethod
    def obtener_grupos(self, email: str) -> dict[str, str]:
        """codigo -> grupo ESIIAB (A, B, C, I, intensificación...)."""

    @abstractmethod
    def obtener_convalidadas(self, email: str) -> set[str]: ...

    @abstractmethod
    def reemplazar_alumno(
        self,
        email: str,
        codigos: list[str],
        grupos: dict[str, str] | None = None,
    ) -> None: ...

    @abstractmethod
    def rellenar_notas(self, email: str, notas: dict[str, float]) -> None: ...

    @abstractmethod
    def marcar_convalidadas(self, email: str, codigos: list[str]) -> None: ...
