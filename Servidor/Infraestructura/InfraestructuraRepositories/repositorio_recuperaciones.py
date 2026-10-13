from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Servidor.Dominio.DominioEntities.recuperacion import Recuperacion


class RepositorioRecuperaciones(ABC):
    @abstractmethod
    def guardar(self, recuperacion: Recuperacion) -> Recuperacion: ...

    @abstractmethod
    def obtener(self, token: str) -> Recuperacion | None: ...

    @abstractmethod
    def eliminar(self, token: str) -> None: ...

    @abstractmethod
    def eliminar_por_email(self, email: str) -> None: ...

    @abstractmethod
    def actualizar_email(self, email_actual: str, email_nuevo: str) -> None: ...
