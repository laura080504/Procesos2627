from __future__ import annotations

from Servidor.Dominio.DominioEntities.asignatura import Asignatura
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas import RepositorioAsignaturas


class RepositorioAsignaturasMemoria(RepositorioAsignaturas):
    def __init__(self):
        self._asignaturas: dict[str, Asignatura] = {}

    def obtener_todas(self) -> list[Asignatura]:
        return list(self._asignaturas.values())

    def reemplazar(self, asignaturas: list[Asignatura]) -> None:
        self._asignaturas = {asignatura.codigo: asignatura for asignatura in asignaturas}
