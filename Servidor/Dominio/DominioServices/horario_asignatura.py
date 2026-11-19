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


def franjas_de(
    asignaturas: list[Asignatura],
    grupos_por_codigo: dict[str, str] | None = None,
) -> list[FranjaHorario]:
    """Cruza asignaturas matriculadas con el horario ESIIAB.

    Acepta grupos ESIIAB (A/B/ING. SOFTWARE) o números de campus (11, 14…).
    """
    franjas = []
    grupos = grupos_por_codigo or {}
    mapa = mapa_sesiones()
    for asignatura in asignaturas:
        grupo_alumno = (grupos.get(asignatura.codigo) or "").strip()
        sesiones = _sesiones_por_nombre(mapa, asignatura.nombre)
        filtro = _grupo_filtro(grupo_alumno, sesiones)
        for dia, inicio, fin, tipo, aula, grupo in _desempaquetar(sesiones):
            if filtro and grupo and filtro != grupo:
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
                    grupo or filtro or grupo_alumno,
                )
            )
    franjas.sort(key=lambda franja: (franja.dia, franja.inicio, franja.codigo, franja.grupo))
    return franjas


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


def _grupo_filtro(grupo_alumno: str, sesiones: tuple) -> str | None:
    if not grupo_alumno:
        return None
    disponibles = {sesion[5] for sesion in _desempaquetar(sesiones) if sesion[5]}
    if grupo_alumno in disponibles:
        return grupo_alumno
    for candidato in _MAPA_GRUPO_CAMPUS.get(grupo_alumno, ()):
        if candidato in disponibles:
            return candidato
    # Solo para números de campus sin mapa: si la asignatura tiene un único grupo ESIIAB.
    if grupo_alumno.isdigit() and len(disponibles) == 1:
        return next(iter(disponibles))
    return grupo_alumno


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


def _desempaquetar(sesiones) -> list[tuple[int, str, str, str, str, str]]:
    resultado = []
    for sesion in sesiones:
        if len(sesion) >= 6:
            resultado.append((sesion[0], sesion[1], sesion[2], sesion[3], sesion[4], sesion[5]))
        elif len(sesion) == 5:
            resultado.append((sesion[0], sesion[1], sesion[2], sesion[3], sesion[4], ""))
        else:
            dia, inicio, fin, tipo = sesion[:4]
            resultado.append((dia, inicio, fin, tipo, "", ""))
    return resultado
