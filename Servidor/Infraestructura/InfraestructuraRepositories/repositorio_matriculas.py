from __future__ import annotations

from abc import ABC, abstractmethod


class RepositorioMatriculas(ABC):
    @abstractmethod
    def obtener_codigos(self, email: str) -> list[str]:
        """Códigos de la matrícula activa (curso actual / agenda)."""

    @abstractmethod
    def obtener_notas(self, email: str) -> dict[str, float | None]:
        """Notas de matrícula activa + historial académico."""

    @abstractmethod
    def obtener_grupos(self, email: str) -> dict[str, str]:
        """codigo -> grupo ESIIAB (A, B, C, I, intensificación...). Solo activas."""

    @abstractmethod
    def obtener_convalidadas(self, email: str) -> set[str]: ...

    @abstractmethod
    def reemplazar_alumno(
        self,
        email: str,
        codigos: list[str],
        grupos: dict[str, str] | None = None,
    ) -> None:
        """Sustituye la matrícula activa; conserva notas e historial calificado."""

    @abstractmethod
    def rellenar_notas(self, email: str, notas: dict[str, float]) -> None: ...

    @abstractmethod
    def sincronizar_calificaciones(
        self,
        email: str,
        notas: dict[str, float | None],
        convalidadas: set[str] | frozenset[str],
    ) -> None:
        """Sustituye el expediente calificado (manual). Conserva matrícula activa."""

    @abstractmethod
    def marcar_convalidadas(self, email: str, codigos: list[str]) -> None: ...

    @abstractmethod
    def vaciar_todos_excepto(self, email: str) -> None: ...
