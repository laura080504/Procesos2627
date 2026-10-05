from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from servidor.logica.entities.usuario import Usuario


class RepositorioUsuarios(ABC):
    """Contrato de la capa de datos. Los use cases solo dependen de esta interfaz."""

    @abstractmethod
    def insertar(self, usuario: Usuario) -> Usuario: ...

    @abstractmethod
    def obtener_por_email(self, email: str) -> Usuario | None: ...

    @abstractmethod
    def obtener_todos(self) -> list[Usuario]: ...

    @abstractmethod
    def eliminar(self, email: str) -> bool: ...
