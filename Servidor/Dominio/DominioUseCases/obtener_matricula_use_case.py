from dataclasses import dataclass

from Servidor.Dominio.DominioEntities.asignatura import Asignatura
from Servidor.Dominio.DominioEnums.curso_asignatura import CursoAsignatura
from Servidor.Dominio.DominioServices.curso_alumno import curso_del_alumno
from Servidor.Dominio.DominioServices.expediente_alumno import expediente_de
from Servidor.Dominio.DominioServices.horario_asignatura import FranjaHorario, franjas_de
from Servidor.Dominio.DominioServices.matriculas_muestra import TramoCurso, asegurar_matricula_de, tramos_de
from Servidor.Dominio.DominioServices.normalizar_texto import normalizar_texto
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas import RepositorioAsignaturas
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas import RepositorioMatriculas


@dataclass(frozen=True)
class MatriculaAlumno:
    curso: CursoAsignatura | None
    tramos: list[TramoCurso]
    asignaturas: list[Asignatura]
    creditos_aprobados: int
    media: float | None
    horario: list[FranjaHorario]


class ObtenerMatriculaUseCase:
    def __init__(self, repositorio_matriculas: RepositorioMatriculas, repositorio_asignaturas: RepositorioAsignaturas):
        self.repositorio_matriculas = repositorio_matriculas
        self.repositorio_asignaturas = repositorio_asignaturas

    def ejecutar(self, email: str, nombre: str = "") -> MatriculaAlumno:
        asegurar_matricula_de(self.repositorio_matriculas, email)
        notas = self.repositorio_matriculas.obtener_notas(email)
        catalogo = self.repositorio_asignaturas.obtener_todas()
        propias = [asignatura for asignatura in catalogo if asignatura.codigo in notas]
        expediente = expediente_de(propias, notas)
        visibles = _filtrar_por_nombre(propias, nombre)
        visibles.sort(key=lambda asignatura: asignatura.codigo)
        return MatriculaAlumno(
            curso_del_alumno(propias),
            tramos_de(propias),
            visibles,
            expediente.creditos_aprobados,
            expediente.media,
            franjas_de(propias),
        )


def _filtrar_por_nombre(asignaturas: list[Asignatura], nombre: str) -> list[Asignatura]:
    busqueda = normalizar_texto(nombre)
    if not busqueda:
        return list(asignaturas)
    return [
        asignatura
        for asignatura in asignaturas
        if busqueda in normalizar_texto(asignatura.nombre)
        or busqueda in normalizar_texto(asignatura.nombre_ingles)
    ]
