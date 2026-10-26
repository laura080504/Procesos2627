from __future__ import annotations

from Servidor.Dominio.DominioEntities.asignatura import Asignatura
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_cursos import RepositorioCursos


class RepositorioCursosMemoria(RepositorioCursos):
    def __init__(self):
        self._por_curso: dict[str, dict[str, Asignatura]] = {}

    def obtener(self, curso: str) -> list[Asignatura]:
        return sorted(self._por_curso.get(curso, {}).values(), key=lambda asignatura: asignatura.codigo)

    def guardar(self, asignatura: Asignatura) -> None:
        self._por_curso.setdefault(asignatura.curso.value, {})[asignatura.codigo] = asignatura
