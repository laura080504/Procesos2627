from __future__ import annotations

from dataclasses import dataclass

from Servidor.Dominio.DominioExceptions.estado_no_valido import EstadoNoValido
from Servidor.Dominio.DominioUseCases.obtener_matricula_use_case import MatriculaAlumno, ObtenerMatriculaUseCase
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas import RepositorioAsignaturas
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas import RepositorioMatriculas


@dataclass(frozen=True)
class AsignaturaMatriculaEntrada:
    codigo: str
    grupo: str


class GuardarMatriculaUseCase:
    def __init__(
        self,
        repositorio_matriculas: RepositorioMatriculas,
        repositorio_asignaturas: RepositorioAsignaturas,
        obtener_matricula: ObtenerMatriculaUseCase,
    ):
        self.repositorio_matriculas = repositorio_matriculas
        self.repositorio_asignaturas = repositorio_asignaturas
        self.obtener_matricula = obtener_matricula

    def ejecutar(self, email: str, asignaturas: list[AsignaturaMatriculaEntrada]) -> MatriculaAlumno:
        if not asignaturas:
            raise EstadoNoValido("Debes indicar al menos una asignatura matriculada.")

        catalogo = {asignatura.codigo: asignatura for asignatura in self.repositorio_asignaturas.obtener_todas()}
        codigos: list[str] = []
        grupos: dict[str, str] = {}
        vistos: set[str] = set()

        for item in asignaturas:
            codigo = (item.codigo or "").strip()
            grupo = (item.grupo or "A").strip().upper() or "A"
            if not codigo:
                raise EstadoNoValido("Cada asignatura necesita un código.")
            if codigo not in catalogo:
                raise EstadoNoValido(f"La asignatura {codigo} no está en el catálogo.")
            if codigo in vistos:
                raise EstadoNoValido(f"La asignatura {codigo} está repetida.")
            if len(grupo) > 24:
                raise EstadoNoValido(f"El grupo de {codigo} no es válido.")
            vistos.add(codigo)
            codigos.append(codigo)
            grupos[codigo] = grupo

        self.repositorio_matriculas.reemplazar_alumno(email, codigos, grupos)
        self.obtener_matricula.invalidar_cache(email)
        return self.obtener_matricula.ejecutar(email)
