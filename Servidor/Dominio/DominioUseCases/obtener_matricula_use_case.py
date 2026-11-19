from dataclasses import dataclass

from Servidor.Dominio.DominioEntities.asignatura import Asignatura
from Servidor.Dominio.DominioEnums.curso_asignatura import CursoAsignatura
from Servidor.Dominio.DominioServices.curso_alumno import curso_del_alumno
from Servidor.Dominio.DominioServices.expediente_alumno import expediente_de
from Servidor.Dominio.DominioServices.horario_asignatura import FranjaHorario, aulas_de, franjas_de
from Servidor.Dominio.DominioServices.matriculas_muestra import TramoCurso, asegurar_matricula_de, tramos_de
from Servidor.Dominio.DominioServices.normalizar_texto import normalizar_texto
from Servidor.Dominio.DominioServices.parser_ficha_esiiab import FichaEsiiab
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas import RepositorioAsignaturas
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas import RepositorioMatriculas


@dataclass(frozen=True)
class AsignaturaMatricula:
    codigo: str
    nombre: str
    nombre_ingles: str
    curso: CursoAsignatura
    creditos: int
    cuatrimestre: int
    grupo: str
    url_esiiab: str | None
    profesores: tuple
    aulas_teoria: tuple[str, ...]
    aulas_practicas: tuple[str, ...]


@dataclass(frozen=True)
class MatriculaAlumno:
    curso: CursoAsignatura | None
    tramos: list[TramoCurso]
    asignaturas: list[AsignaturaMatricula]
    creditos_aprobados: int
    creditos_convalidados: int
    media: float | None
    horario: list[FranjaHorario]


class ObtenerMatriculaUseCase:
    def __init__(
        self,
        repositorio_matriculas: RepositorioMatriculas,
        repositorio_asignaturas: RepositorioAsignaturas,
        cliente_esiiab=None,
    ):
        self.repositorio_matriculas = repositorio_matriculas
        self.repositorio_asignaturas = repositorio_asignaturas
        self.cliente_esiiab = cliente_esiiab

    def ejecutar(self, email: str, nombre: str = "") -> MatriculaAlumno:
        asegurar_matricula_de(self.repositorio_matriculas, email)
        notas = self.repositorio_matriculas.obtener_notas(email)
        grupos = self.repositorio_matriculas.obtener_grupos(email)
        convalidadas = self.repositorio_matriculas.obtener_convalidadas(email)
        catalogo = self.repositorio_asignaturas.obtener_todas()
        propias = [asignatura for asignatura in catalogo if asignatura.codigo in notas]
        expediente = expediente_de(propias, notas, convalidadas)
        visibles = _filtrar_por_nombre(propias, nombre)
        visibles.sort(key=lambda asignatura: asignatura.codigo)
        horario = franjas_de(propias, grupos)
        fichas = self._fichas(visibles)
        urls = self._urls()
        enriquecidas = [
            _enriquecer(
                asignatura,
                horario,
                grupos.get(asignatura.codigo, "A"),
                fichas.get(asignatura.codigo),
                urls.get(normalizar_texto(asignatura.nombre)),
            )
            for asignatura in visibles
        ]
        return MatriculaAlumno(
            curso_del_alumno(propias),
            tramos_de(propias),
            enriquecidas,
            expediente.creditos_aprobados,
            expediente.creditos_convalidados,
            expediente.media,
            horario,
        )

    def _fichas(self, asignaturas: list[Asignatura]) -> dict[str, FichaEsiiab]:
        if self.cliente_esiiab is None or not asignaturas:
            return {}
        return self.cliente_esiiab.fichas_de([(a.codigo, a.nombre) for a in asignaturas])

    def _urls(self) -> dict[str, str]:
        if self.cliente_esiiab is None:
            return {}
        return self.cliente_esiiab.urls_asignaturas()


def _enriquecer(
    asignatura: Asignatura,
    horario: list[FranjaHorario],
    grupo: str,
    ficha: FichaEsiiab | None,
    url: str | None,
) -> AsignaturaMatricula:
    aulas_teoria, aulas_practicas = aulas_de(horario, asignatura.codigo, grupo)
    profesores = tuple(ficha.profesores) if ficha else ()
    return AsignaturaMatricula(
        asignatura.codigo,
        asignatura.nombre,
        asignatura.nombre_ingles,
        asignatura.curso,
        asignatura.creditos,
        asignatura.cuatrimestre,
        grupo or "A",
        (ficha.url if ficha and ficha.url else url),
        profesores,
        tuple(aulas_teoria),
        tuple(aulas_practicas),
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
