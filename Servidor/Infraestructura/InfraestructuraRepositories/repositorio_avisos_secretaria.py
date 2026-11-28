from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Servidor.Dominio.DominioEntities.aviso_secretaria import AvisoSecretaria


class RepositorioAvisosSecretaria(ABC):
    @abstractmethod
    def obtener_todos(self) -> list[AvisoSecretaria]: ...

    @abstractmethod
    def obtener_por_id(self, aviso_id: str) -> AvisoSecretaria | None: ...

    @abstractmethod
    def guardar(self, aviso: AvisoSecretaria) -> AvisoSecretaria: ...

    @abstractmethod
    def eliminar(self, aviso_id: str) -> bool: ...

    @abstractmethod
    def vacio(self) -> bool: ...
