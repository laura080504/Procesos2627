from dataclasses import dataclass
from datetime import date
from time import monotonic

from Servidor.Dominio.DominioEntities.asignatura import Asignatura
from Servidor.Dominio.DominioEnums.curso_asignatura import CursoAsignatura
from Servidor.Dominio.DominioServices.cuatrimestre_actual import cuatrimestre_actual
from Servidor.Dominio.DominioServices.curso_alumno import curso_del_alumno
from Servidor.Dominio.DominioServices.expediente_alumno import expediente_de
from Servidor.Dominio.DominioServices.franjas_tutorias import franjas_tutorias_de
from Servidor.Dominio.DominioServices.horario_asignatura import FranjaHorario, aulas_de, franjas_de
from Servidor.Dominio.DominioServices.matriculas_muestra import TramoCurso, asegurar_matricula_de, tramos_de
from Servidor.Dominio.DominioServices.normalizar_texto import normalizar_texto
from Servidor.Dominio.DominioServices.parser_ficha_esiiab import FichaEsiiab, ProfesorEsiiab
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaturas import RepositorioAsignaturas
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_docencia import RepositorioDocencia
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
    intensificacion: str | None = None
    modo: str = "alumno"
    nombre_docente: str | None = None
    # Fecha real del PC → tutorías de ficha. El cliente filtra horario por semana vista.
    cuatrimestre_actual: int = 1
    inicio_segundo: str | None = None


class ObtenerMatriculaUseCase:
    def __init__(
        self,
        repositorio_matriculas: RepositorioMatriculas,
        repositorio_asignaturas: RepositorioAsignaturas,
        cliente_esiiab=None,
        repositorio_docencia: RepositorioDocencia | None = None,
    ):
        self.repositorio_matriculas = repositorio_matriculas
        self.repositorio_asignaturas = repositorio_asignaturas
        self.cliente_esiiab = cliente_esiiab
        self.repositorio_docencia = repositorio_docencia
        self._cache: dict[tuple[str, str], tuple[float, MatriculaAlumno]] = {}
        self._catalogo_cache: tuple[float, list[Asignatura]] | None = None
        self._periodo_cache: tuple[date, int, str | None] | None = None

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

        codigos_docencia = (
            self.repositorio_docencia.obtener_codigos(email) if self.repositorio_docencia is not None else []
        )
        if codigos_docencia:
            resultado = self._agenda_profesor(email, codigos_docencia, nombre, ahora)
        else:
            resultado = self._agenda_alumno(email, nombre, ahora)

        self._cache[clave] = (ahora, resultado)
        if len(self._cache) > 64:
            antiguas = sorted(self._cache.items(), key=lambda item: item[1][0])[:16]
            for vieja, _ in antiguas:
                self._cache.pop(vieja, None)
        return resultado

    def _agenda_alumno(self, email: str, nombre: str, ahora: float) -> MatriculaAlumno:
        asegurar_matricula_de(self.repositorio_matriculas, email)
        notas = self.repositorio_matriculas.obtener_notas(email)
        grupos = self.repositorio_matriculas.obtener_grupos(email)
        convalidadas = self.repositorio_matriculas.obtener_convalidadas(email)
        catalogo = self._catalogo(ahora)
        activas = set(self.repositorio_matriculas.obtener_codigos(email))
        propias = [asignatura for asignatura in catalogo if asignatura.codigo in activas]
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
        visibles = _filtrar_por_nombre(propias, nombre)
        visibles.sort(key=lambda asignatura: asignatura.codigo)
        # Horario: ambos cuatrimestres (el cliente filtra por la semana navegada).
        horario = franjas_de(propias, grupos)
        periodo_ficha, inicio_segundo = self._periodo_real()
        fichas, urls = self._datos_esiiab(visibles)
        enriquecidas = [
            _enriquecer(
                asignatura,
                horario,
                grupos.get(asignatura.codigo, "A"),
                fichas.get(asignatura.codigo),
                urls.get(normalizar_texto(asignatura.nombre)),
                periodo_ficha,
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
            self.repositorio_matriculas.obtener_intensificacion(email),
            "alumno",
            None,
            periodo_ficha,
            inicio_segundo,
        )

    def _agenda_profesor(
        self,
        email: str,
        codigos: list[str],
        nombre: str,
        ahora: float,
    ) -> MatriculaAlumno:
        catalogo = self._catalogo(ahora)
        por_codigo = {asignatura.codigo: asignatura for asignatura in catalogo}
        propias = [por_codigo[codigo] for codigo in codigos if codigo in por_codigo]
        visibles = _filtrar_por_nombre(propias, nombre)
        visibles.sort(key=lambda asignatura: asignatura.codigo)
        # Clases de ambos cuatrimestres; tutorías etiquetadas por cuatrimestre.
        horario = franjas_de(propias, {})
        periodo_ficha, inicio_segundo = self._periodo_real()
        fichas, urls = self._datos_esiiab(visibles)
        nombre_docente = (
            self.repositorio_docencia.obtener_nombre_docente(email) if self.repositorio_docencia else None
        )
        enriquecidas = [
            _enriquecer(
                asignatura,
                horario,
                "",
                fichas.get(asignatura.codigo),
                urls.get(normalizar_texto(asignatura.nombre)),
                periodo_ficha,
            )
            for asignatura in visibles
        ]
        horario_completo = list(horario)
        for asignatura in propias:
            ficha = fichas.get(asignatura.codigo)
            if not ficha:
                continue
            for profesor in ficha.profesores:
                if nombre_docente and normalizar_texto(profesor.nombre) != normalizar_texto(nombre_docente):
                    continue
                for periodo in (1, 2):
                    if asignatura.cuatrimestre and asignatura.cuatrimestre != periodo:
                        continue
                    horario_completo.extend(
                        franjas_tutorias_de(
                            asignatura.codigo,
                            asignatura.nombre,
                            asignatura.nombre_ingles,
                            profesor.tutorias_de(periodo),
                            periodo,
                        )
                    )
        horario_completo.sort(
            key=lambda franja: (franja.cuatrimestre, franja.dia, franja.inicio, franja.codigo, franja.tipo)
        )
        return MatriculaAlumno(
            curso_del_alumno(propias),
            tramos_de(propias),
            enriquecidas,
            0,
            0,
            None,
            horario_completo,
            None,
            "profesor",
            nombre_docente,
            periodo_ficha,
            inicio_segundo,
        )

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

    def _periodo_real(self) -> tuple[int, str | None]:
        """Cuatrimestre según la fecha real del sistema + inicio del 2.º (ISO)."""
        hoy = date.today()
        if self._periodo_cache and self._periodo_cache[0] == hoy:
            return self._periodo_cache[1], self._periodo_cache[2]
        calendario = None
        if self.cliente_esiiab is not None and hasattr(self.cliente_esiiab, "asegurar_calendario"):
            calendario = self.cliente_esiiab.asegurar_calendario()
        periodo = cuatrimestre_actual(hoy, calendario)
        inicio_segundo = _inicio_segundo_iso(calendario)
        self._periodo_cache = (hoy, periodo, inicio_segundo)
        return periodo, inicio_segundo


def _inicio_segundo_iso(calendario) -> str | None:
    if calendario is None:
        return None
    inicios = [
        fecha.inicio
        for fecha in calendario.fechas
        if fecha.tipo == "inicio_cuatrimestre" and "segundo" in fecha.titulo.casefold()
    ]
    if not inicios:
        return None
    return min(inicios).isoformat()


def _enriquecer(
    asignatura: Asignatura,
    horario: list[FranjaHorario],
    grupo: str,
    ficha: FichaEsiiab | None,
    url: str | None,
    cuatrimestre_vigente: int,
) -> AsignaturaMatricula:
    aulas_teoria, aulas_practicas = aulas_de(horario, asignatura.codigo, grupo or None)
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
        grupo or "",
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
