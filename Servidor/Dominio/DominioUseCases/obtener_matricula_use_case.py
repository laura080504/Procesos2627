from dataclasses import dataclass

from Servidor.Dominio.DominioEntities.asignatura import Asignatura
from Servidor.Dominio.DominioEnums.curso_asignatura import CursoAsignatura
from Servidor.Dominio.DominioServices.curso_alumno import curso_del_alumno
from Servidor.Dominio.DominioServices.expediente_alumno import expediente_de
from Servidor.Dominio.DominioServices.horario_asignatura import FranjaHorario, franjas_de
from Servidor.Dominio.DominioServices.matriculas_muestra import TramoCurso, tramos_de
from Servidor.Dominio.DominioUseCases.listar_asignaturas_use_case import _plano
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
        notas = self.repositorio_matriculas.obtener_notas(email)
        catalogo = self.repositorio_asignaturas.obtener_todas()
        propias = [asignatura for asignatura in catalogo if asignatura.codigo in notas]
        expediente = expediente_de(propias, notas)
        busqueda = _plano(nombre)
        visibles = propias
        if busqueda:
            visibles = [
                asignatura
                for asignatura in propias
                if busqueda in _plano(asignatura.nombre) or busqueda in _plano(asignatura.nombre_ingles)
            ]
        visibles.sort(key=lambda asignatura: asignatura.codigo)
        return MatriculaAlumno(
            curso_del_alumno(propias),
            tramos_de(propias),
            visibles,
            expediente.creditos_aprobados,
            expediente.media,
            franjas_de(propias),
        )
