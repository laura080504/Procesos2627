from __future__ import annotations

from typing import Protocol

from Servidor.Dominio.DominioEntities.asignacion_rol import AsignacionRol


class RepositorioAsignacionesRol(Protocol):
    def guardar(self, asignacion: AsignacionRol) -> AsignacionRol: ...

    def obtener(self, token: str) -> AsignacionRol | None: ...

    def eliminar(self, token: str) -> None: ...

    def eliminar_por_email(self, email: str) -> None: ...
