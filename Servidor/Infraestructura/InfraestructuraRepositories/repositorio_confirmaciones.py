from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Servidor.Dominio.DominioEntities.confirmacion import Confirmacion


class RepositorioConfirmaciones(ABC):
    @abstractmethod
    def guardar(self, confirmacion: Confirmacion) -> Confirmacion: ...

    @abstractmethod
    def obtener(self, token: str) -> Confirmacion | None: ...

    @abstractmethod
    def eliminar(self, token: str) -> None: ...

    @abstractmethod
    def eliminar_por_email(self, email: str) -> None: ...
