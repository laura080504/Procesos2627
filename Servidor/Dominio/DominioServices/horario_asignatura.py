from dataclasses import dataclass

from Servidor.Dominio.DominioEntities.asignatura import Asignatura
from Servidor.Dominio.DominioServices.horario_esiiab import mapa_sesiones
from Servidor.Dominio.DominioServices.normalizar_texto import normalizar_texto

# Número de grupo del campus UCLM → etiquetas ESIIAB (cabeceras "GRUPO B (11)").
_MAPA_GRUPO_CAMPUS: dict[str, tuple[str, ...]] = {
    "10": ("A",),
    "11": ("B",),
    "12": ("C", "I"),
    "13": ("I",),
    "14": ("ING. SOFTWARE",),
    "17": ("O1",),
}
_STOP = {"de", "la", "el", "en", "y", "del", "las", "los", "un", "una"}


@dataclass(frozen=True)
class FranjaHorario:
    codigo: str
    nombre: str
    nombre_ingles: str
    dia: int
    inicio: str
    fin: str
    tipo: str
    aula: str = ""
    grupo: str = ""
    cuatrimestre: int = 0


def franjas_de(
    asignaturas: list[Asignatura],
    grupos_por_codigo: dict[str, str] | None = None,
) -> list[FranjaHorario]:
    """Cruza asignaturas matriculadas con el horario ESIIAB.

    Acepta grupos ESIIAB (A/B/ING. SOFTWARE) o números de campus (11, 14…).
    Cada franja lleva el cuatrimestre de la asignatura para filtrar por semana vista.
    Fusiona huecos contiguos del mismo bloque (p. ej. 11:35–13:05 + 13:05–14:35).
    """
    franjas = []
    grupos = grupos_por_codigo or {}
    mapa = mapa_sesiones()
    for asignatura in asignaturas:
        grupo_alumno = (grupos.get(asignatura.codigo) or "").strip()
        crudas = _desempaquetar(_sesiones_por_nombre(mapa, asignatura.nombre))
        del_cuatri = [
            sesion
            for sesion in crudas
            if not sesion[6] or not asignatura.cuatrimestre or sesion[6] == asignatura.cuatrimestre
        ]
        etiquetadas = {sesion[5] for sesion in del_cuatri if sesion[5]}
        filtro = _grupo_filtro(grupo_alumno, del_cuatri)
        for dia, inicio, fin, tipo, aula, grupo, _cuatri in del_cuatri:
            if not _sesion_del_grupo(filtro, grupo, etiquetadas):
                continue
            franjas.append(
                FranjaHorario(
                    asignatura.codigo,
                    asignatura.nombre,
                    asignatura.nombre_ingles,
                    dia,
                    inicio,
                    fin,
                    tipo,
                    aula,
                    _etiqueta_grupo_visible(grupo, filtro),
                    asignatura.cuatrimestre,
                )
            )
    return _fusionar_contiguas(franjas)


def aulas_de(franjas: list[FranjaHorario], codigo: str, grupo: str | None = None) -> tuple[list[str], list[str]]:
    teoria: list[str] = []
    practicas: list[str] = []
    filtro = (grupo or "").strip()
    candidatos = {filtro, *_MAPA_GRUPO_CAMPUS.get(filtro, ())} if filtro else set()
    for franja in franjas:
        if franja.codigo != codigo or not franja.aula:
            continue
        if candidatos and franja.grupo and franja.grupo not in candidatos:
            continue
        destino = practicas if franja.tipo == "practicas" else teoria
        if franja.aula not in destino:
            destino.append(franja.aula)
    return teoria, practicas


def _grupo_filtro(grupo_alumno: str, sesiones) -> str | None:
    if not grupo_alumno:
        return None
    desempaquetadas = (
        sesiones
        if isinstance(sesiones, list)
        and sesiones
        and isinstance(sesiones[0], tuple)
        and len(sesiones[0]) >= 6
        else _desempaquetar(sesiones)
    )
    disponibles = {sesion[5] for sesion in desempaquetadas if sesion[5]}
    if grupo_alumno in disponibles:
        return grupo_alumno
    for candidato in _MAPA_GRUPO_CAMPUS.get(grupo_alumno, ()):
        if candidato in disponibles:
            return candidato
    # Solo para números de campus sin mapa: si la asignatura tiene un único grupo ESIIAB.
    if grupo_alumno.isdigit() and len(disponibles) == 1:
        return next(iter(disponibles))
    return grupo_alumno


def _sesion_del_grupo(filtro: str | None, grupo: str, etiquetadas: set[str]) -> bool:
    """Incluye la sesión si encaja con el grupo del alumno.

    - Sin filtro (matrícula sin grupo u horario único): todas.
    - Con filtro: solo la etiqueta ESIIAB coincidente.
    - Si la asignatura tiene grupos etiquetados, se ignoran filas sin grupo.
    """
    if not filtro:
        return True
    if not grupo:
        return not etiquetadas
    if grupo == filtro:
        return True
    return grupo in _MAPA_GRUPO_CAMPUS.get(filtro, ())


def _etiqueta_grupo_visible(grupo_esiiab: str, filtro: str | None) -> str:
    """No pintar el código numérico de campus (10/11…) como si fuera grupo ESIIAB."""
    if grupo_esiiab:
        return grupo_esiiab
    if filtro and not str(filtro).isdigit():
        return filtro
    return ""


def _fusionar_contiguas(franjas: list[FranjaHorario]) -> list[FranjaHorario]:
    if not franjas:
        return []
    ordenadas = sorted(
        franjas,
        key=lambda franja: (
            franja.codigo,
            franja.dia,
            franja.tipo,
            franja.grupo,
            franja.aula,
            franja.cuatrimestre,
            franja.inicio,
            franja.fin,
        ),
    )
    resultado: list[FranjaHorario] = []
    actual = ordenadas[0]
    for siguiente in ordenadas[1:]:
        misma = (
            actual.codigo == siguiente.codigo
            and actual.dia == siguiente.dia
            and actual.tipo == siguiente.tipo
            and actual.grupo == siguiente.grupo
            and actual.aula == siguiente.aula
            and actual.cuatrimestre == siguiente.cuatrimestre
            and actual.fin == siguiente.inicio
        )
        if misma:
            actual = FranjaHorario(
                actual.codigo,
                actual.nombre,
                actual.nombre_ingles,
                actual.dia,
                actual.inicio,
                siguiente.fin,
                actual.tipo,
                actual.aula,
                actual.grupo,
                actual.cuatrimestre,
            )
        else:
            resultado.append(actual)
            actual = siguiente
    resultado.append(actual)
    resultado.sort(key=lambda franja: (franja.dia, franja.inicio, franja.codigo, franja.grupo))
    return resultado


def _sesiones_por_nombre(mapa: dict[str, tuple], nombre: str) -> tuple:
    clave = normalizar_texto(nombre)
    if clave in mapa:
        return mapa[clave]
    for alternativa in (clave.replace(" de ", " en "), clave.replace(" en ", " de ")):
        if alternativa in mapa:
            return mapa[alternativa]
    tokens = {token for token in clave.split() if token not in _STOP}
    if not tokens:
        return ()
    mejor = ()
    puntuacion = 0
    for clave_mapa, sesiones in mapa.items():
        propios = {token for token in clave_mapa.split() if token not in _STOP}
        score = len(tokens & propios)
        if score >= max(2, len(tokens) - 1) and score > puntuacion:
            mejor = sesiones
            puntuacion = score
    return mejor


def _desempaquetar(sesiones) -> list[tuple[int, str, str, str, str, str, int]]:
    resultado = []
    for sesion in sesiones:
        if len(sesion) >= 7:
            resultado.append(
                (sesion[0], sesion[1], sesion[2], sesion[3], sesion[4], sesion[5], int(sesion[6] or 0))
            )
        elif len(sesion) == 6:
            resultado.append((sesion[0], sesion[1], sesion[2], sesion[3], sesion[4], sesion[5], 0))
        elif len(sesion) == 5:
            resultado.append((sesion[0], sesion[1], sesion[2], sesion[3], sesion[4], "", 0))
        else:
            dia, inicio, fin, tipo = sesion[:4]
            resultado.append((dia, inicio, fin, tipo, "", "", 0))
    return resultado
