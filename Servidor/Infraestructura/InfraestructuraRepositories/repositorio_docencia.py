from __future__ import annotations

from abc import ABC, abstractmethod


class RepositorioDocencia(ABC):
    @abstractmethod
    def obtener_codigos(self, email: str) -> list[str]:
        """Asignaturas que imparte ese profesor."""

    @abstractmethod
    def obtener_nombre_docente(self, email: str) -> str | None:
        """Nombre ESIIAB del profesor, si está guardado."""

    @abstractmethod
    def reemplazar(
        self,
        email: str,
        codigos: list[str],
        nombre_docente: str | None = None,
    ) -> None: ...

    @abstractmethod
    def cambiar_email(self, email_actual: str, email_nuevo: str) -> None:
        """Pasa las asignaturas que imparte al correo nuevo."""
