"""Parser del calendario académico público de la ESIIAB."""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from datetime import date, timedelta
from html import unescape

_ITEM = re.compile(
    "data-category=\"(\\d+)\".*?wpsc-important-date-date\">([^<]+)</div>"
    ".*?wpsc-important-date-title\">(.*?)</div>",
    re.S,
)
_FECHA = re.compile(r"(\d{1,2})/(\d{1,2})/(\d{4})")
_RANGO = re.compile(
    r"(\d{1,2}/\d{1,2}/\d{4})\s*-\s*(\d{1,2}/\d{1,2}/\d{4})"
)

_FESTIVO_CLAVE = (
    "fiesta",
    "día de",
    "dia de",
    "navidad",
    "semana santa",
    "corpus",
    "vacaciones",
    "inmaculada",
    "santo tomás",
    "santo tomas",
    "fieles difuntos",
    "castilla-la mancha",
    "castilla la mancha",
)


@dataclass(frozen=True)
class FechaAcademica:
    tipo: str
    titulo: str
    inicio: date
    fin: date


@dataclass(frozen=True)
class CalendarioAcademicoEsiiab:
    fechas: tuple[FechaAcademica, ...]
    curso: str = ""


def parsear_calendario_html(contenido: str) -> CalendarioAcademicoEsiiab:
    vistos: set[tuple[str, date, date]] = set()
    fechas: list[FechaAcademica] = []
    for _categoria, bruto_fecha, bruto_titulo in _ITEM.findall(contenido):
        titulo = unescape(re.sub(r"<[^>]+>", "", bruto_titulo)).strip()
        if not titulo:
            continue
        inicio, fin = _parsear_rango(bruto_fecha.strip())
        if inicio is None:
            continue
        clave = (titulo.casefold(), inicio, fin)
        if clave in vistos:
            continue
        vistos.add(clave)
        fechas.append(FechaAcademica(_clasificar(titulo), titulo, inicio, fin))
    fechas.sort(key=lambda item: (item.inicio, item.fin, item.titulo))
    curso = _detectar_curso(contenido, fechas)
    return CalendarioAcademicoEsiiab(tuple(fechas), curso)


def dias_marcados(calendario: CalendarioAcademicoEsiiab, anio: int, mes: int) -> dict[int, list[FechaAcademica]]:
    """Expande rangos a días del mes pedido."""
    por_dia: dict[int, list[FechaAcademica]] = {}
    for fecha in calendario.fechas:
        actual = fecha.inicio
        while actual <= fecha.fin:
            if actual.year == anio and actual.month == mes:
                por_dia.setdefault(actual.day, []).append(fecha)
            actual += timedelta(days=1)
            if actual - fecha.inicio > timedelta(days=120):
                break
    return por_dia


def _clasificar(titulo: str) -> str:
    bajo = titulo.casefold()
    plano = (
        bajo.replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )
    if "cierre de actas" in plano:
        return "academico"
    if any(clave in plano for clave in _FESTIVO_CLAVE):
        if "vacaciones" in plano or "navidad" in plano or "semana santa" in plano:
            return "vacaciones"
        return "festivo"
    if "inicio" in plano and "clases" in plano and "cuatrimestre" in plano:
        return "inicio_cuatrimestre"
    if "fin" in plano and "clases" in plano and "cuatrimestre" in plano:
        return "fin_cuatrimestre"
    if "extraordinari" in plano and "examen" in plano:
        if "inicio" in plano:
            return "inicio_examenes_extraordinarios"
        if "fin" in plano:
            return "fin_examenes_extraordinarios"
        return "examenes_extraordinarios"
    if ("ordinari" in plano or "convocatoria especial" in plano) and "examen" in plano:
        if "inicio" in plano:
            return "inicio_examenes_ordinarios"
        if "fin" in plano:
            return "fin_examenes_ordinarios"
        return "examenes_ordinarios"
    return "academico"


def _parsear_rango(texto: str) -> tuple[date | None, date | None]:
    rango = _RANGO.search(texto)
    if rango:
        inicio = _parsear_fecha(rango.group(1))
        fin = _parsear_fecha(rango.group(2))
        return inicio, fin or inicio
    unica = _FECHA.search(texto)
    if not unica:
        return None, None
    dia = date(int(unica.group(3)), int(unica.group(1)), int(unica.group(2)))
    return dia, dia


def _parsear_fecha(texto: str) -> date | None:
    m = _FECHA.search(texto.strip())
    if not m:
        return None
    return date(int(m.group(3)), int(m.group(1)), int(m.group(2)))


def _detectar_curso(html_bruto: str, fechas: list[FechaAcademica]) -> str:
    m = re.search(r"Calendario\s+(\d{4})\s*[-–]\s*(\d{4})", html.unescape(html_bruto), re.I)
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    if fechas:
        anio = fechas[0].inicio.year
        return f"{anio}-{anio + 1}"
    return ""
