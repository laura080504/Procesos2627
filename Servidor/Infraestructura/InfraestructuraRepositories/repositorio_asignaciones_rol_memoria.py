from __future__ import annotations

from Servidor.Dominio.DominioEntities.asignacion_rol import AsignacionRol
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaciones_rol import (
    RepositorioAsignacionesRol,
)


class RepositorioAsignacionesRolMemoria(RepositorioAsignacionesRol):
    def __init__(self):
        self._asignaciones: dict[str, AsignacionRol] = {}

    def guardar(self, asignacion: AsignacionRol) -> AsignacionRol:
        self._asignaciones[asignacion.token] = asignacion
        return asignacion

    def obtener(self, token: str) -> AsignacionRol | None:
        return self._asignaciones.get(token)

    def eliminar(self, token: str) -> None:
        self._asignaciones.pop(token, None)

    def eliminar_por_email(self, email: str) -> None:
        email = email.strip().lower()
        for token in [t for t, a in self._asignaciones.items() if a.email == email]:
            del self._asignaciones[token]
