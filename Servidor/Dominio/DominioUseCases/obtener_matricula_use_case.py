from dataclasses import dataclass
from datetime import date
from time import monotonic

from Servidor.Dominio.DominioEntities.asignatura import Asignatura
from Servidor.Dominio.DominioEnums.curso_asignatura import CursoAsignatura
from Servidor.Dominio.DominioServices.cuatrimestre_actual import cuatrimestre_actual
from Servidor.Dominio.DominioServices.curso_alumno import curso_del_alumno
from Servidor.Dominio.DominioServices.expediente_alumno import expediente_de
from Servidor.Dominio.DominioServices.horario_asignatura import FranjaHorario, aulas_de, franjas_de
from Servidor.Dominio.DominioServices.matriculas_muestra import TramoCurso, asegurar_matricula_de, tramos_de
from Servidor.Dominio.DominioServices.normalizar_texto import normalizar_texto
from Servidor.Dominio.DominioServices.parser_ficha_esiiab import FichaEsiiab, ProfesorEsiiab
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas import RepositorioAsignaturas
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas import RepositorioMatriculas

_TTL_MATRICULA = 20.0


@dataclass(frozen=True)
class ProfesorMatricula:
    nombre: str
    url: str
    tutorias: tuple[str, ...]


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
    profesores: tuple[ProfesorMatricula, ...]
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
        self._cache: dict[tuple[str, str], tuple[float, MatriculaAlumno]] = {}
        self._catalogo_cache: tuple[float, list[Asignatura]] | None = None
        self._periodo_cache: tuple[date, int] | None = None

    def invalidar_cache(self, email: str | None = None) -> None:
        if email is None:
            self._cache.clear()
            return
        clave = email.strip().lower()
        for guardada in list(self._cache):
            if guardada[0] == clave:
                self._cache.pop(guardada, None)

    def ejecutar(self, email: str, nombre: str = "") -> MatriculaAlumno:
        clave = (email.strip().lower(), normalizar_texto(nombre))
        ahora = monotonic()
        cacheada = self._cache.get(clave)
        if cacheada and ahora - cacheada[0] < _TTL_MATRICULA:
            return cacheada[1]

        asegurar_matricula_de(self.repositorio_matriculas, email)
        notas = self.repositorio_matriculas.obtener_notas(email)
        grupos = self.repositorio_matriculas.obtener_grupos(email)
        convalidadas = self.repositorio_matriculas.obtener_convalidadas(email)
        catalogo = self._catalogo(ahora)
        activas = set(self.repositorio_matriculas.obtener_codigos(email))
        propias = [asignatura for asignatura in catalogo if asignatura.codigo in activas]
        # Expediente / media: matrícula activa + historial calificado.
        del_expediente = [
            asignatura
            for asignatura in catalogo
            if asignatura.codigo in notas
            and (
                asignatura.codigo in activas
                or notas.get(asignatura.codigo) is not None
                or asignatura.codigo in convalidadas
            )
        ]
        expediente = expediente_de(del_expediente, notas, convalidadas)
        resumen = [
            asignatura
            for asignatura in del_expediente
            if notas.get(asignatura.codigo) is not None or asignatura.codigo in convalidadas
        ] or propias
        visibles = _filtrar_por_nombre(propias, nombre)
        visibles.sort(key=lambda asignatura: asignatura.codigo)
        periodo = self._cuatrimestre_hoy()
        # La lista muestra la matrícula activa; el horario solo el cuatrimestre vigente.
        del_periodo = [asignatura for asignatura in propias if asignatura.cuatrimestre == periodo]
        horario = franjas_de(del_periodo, grupos)
        fichas, urls = self._datos_esiiab(visibles)
        enriquecidas = [
            _enriquecer(
                asignatura,
                horario,
                grupos.get(asignatura.codigo, "A"),
                fichas.get(asignatura.codigo),
                urls.get(normalizar_texto(asignatura.nombre)),
                periodo,
            )
            for asignatura in visibles
        ]
        resultado = MatriculaAlumno(
            curso_del_alumno(resumen),
            tramos_de(resumen),
            enriquecidas,
            expediente.creditos_aprobados,
            expediente.creditos_convalidados,
            expediente.media,
            horario,
        )
        self._cache[clave] = (ahora, resultado)
        if len(self._cache) > 64:
            antiguas = sorted(self._cache.items(), key=lambda item: item[1][0])[:16]
            for vieja, _ in antiguas:
                self._cache.pop(vieja, None)
        return resultado

    def _catalogo(self, ahora: float) -> list[Asignatura]:
        if self._catalogo_cache and ahora - self._catalogo_cache[0] < _TTL_MATRICULA:
            return self._catalogo_cache[1]
        catalogo = self.repositorio_asignaturas.obtener_todas()
        self._catalogo_cache = (ahora, catalogo)
        return catalogo

    def _datos_esiiab(self, asignaturas: list[Asignatura]) -> tuple[dict[str, FichaEsiiab], dict[str, str]]:
        if self.cliente_esiiab is None:
            return {}, {}
        urls = self.cliente_esiiab.urls_asignaturas()
        fichas = (
            self.cliente_esiiab.fichas_de([(a.codigo, a.nombre) for a in asignaturas])
            if asignaturas
            else {}
        )
        return fichas, urls

    def _cuatrimestre_hoy(self) -> int:
        """Cuatrimestre académico según la fecha real del sistema."""
        hoy = date.today()
        if self._periodo_cache and self._periodo_cache[0] == hoy:
            return self._periodo_cache[1]
        calendario = None
        if self.cliente_esiiab is not None and hasattr(self.cliente_esiiab, "asegurar_calendario"):
            calendario = self.cliente_esiiab.asegurar_calendario()
        periodo = cuatrimestre_actual(hoy, calendario)
        self._periodo_cache = (hoy, periodo)
        return periodo


def _enriquecer(
    asignatura: Asignatura,
    horario: list[FranjaHorario],
    grupo: str,
    ficha: FichaEsiiab | None,
    url: str | None,
    cuatrimestre_vigente: int,
) -> AsignaturaMatricula:
    aulas_teoria, aulas_practicas = aulas_de(horario, asignatura.codigo, grupo)
    profesores = tuple(
        _profesor_vigente(profesor, cuatrimestre_vigente) for profesor in (ficha.profesores if ficha else ())
    )
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


def _profesor_vigente(profesor: ProfesorEsiiab, cuatrimestre_vigente: int) -> ProfesorMatricula:
    return ProfesorMatricula(
        profesor.nombre,
        profesor.url,
        profesor.tutorias_de(cuatrimestre_vigente),
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
