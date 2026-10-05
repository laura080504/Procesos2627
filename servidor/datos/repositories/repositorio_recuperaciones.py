from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from servidor.logica.entities.recuperacion import Recuperacion


class RepositorioRecuperaciones(ABC):
    @abstractmethod
    def guardar(self, recuperacion: Recuperacion) -> Recuperacion: ...

    @abstractmethod
    def obtener(self, token: str) -> Recuperacion | None: ...

    @abstractmethod
    def eliminar(self, token: str) -> None: ...

    @abstractmethod
    def eliminar_por_email(self, email: str) -> None: ...
