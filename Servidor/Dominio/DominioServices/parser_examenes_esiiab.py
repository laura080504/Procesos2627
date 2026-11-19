"""Parser del calendario de exámenes del grado en la ESIIAB."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from html import unescape

_BLOQUE = re.compile(
    r"<h3 class=\"post-title single-post-title entry-title\"><span>(.*?)</span></h3>"
    r".*?<ul class=\"elementor-icon-list-items elementor-post-info\">(.*?)</ul>",
    re.S,
)
_CAMPO = re.compile(
    r"elementor-post-info__item--type-custom\">\s*([^:<]+):\s*([^<]+)",
    re.S,
)
_FECHA = re.compile(r"(\d{1,2})-(\d{1,2})-(\d{4})")


@dataclass(frozen=True)
class ExamenEsiiab:
    nombre: str
    fecha: date
    hora: str
    centro: str
    aulas: str
    convocatoria: str


@dataclass(frozen=True)
class ExamenesEsiiab:
    examenes: tuple[ExamenEsiiab, ...]


def parsear_examenes_html(contenido: str) -> ExamenesEsiiab:
    ord_pos = contenido.find(">Convocatoria Ordinaria</a>")
    ext_pos = contenido.find(">Convocatoria Extraordinaria</a>")
    examenes: list[ExamenEsiiab] = []
    if ord_pos >= 0:
        fin_ord = ext_pos if ext_pos > ord_pos else len(contenido)
        examenes.extend(_parsear_bloque(contenido[ord_pos:fin_ord], "ordinaria"))
    if ext_pos >= 0:
        examenes.extend(_parsear_bloque(contenido[ext_pos:], "extraordinaria"))
    if not examenes:
        examenes.extend(_parsear_bloque(contenido, "ordinaria"))
    vistos: set[tuple[str, date, str, str]] = set()
    unicos: list[ExamenEsiiab] = []
    for examen in examenes:
        clave = (examen.nombre.casefold(), examen.fecha, examen.hora, examen.convocatoria)
        if clave in vistos:
            continue
        vistos.add(clave)
        unicos.append(examen)
    unicos.sort(key=lambda item: (item.fecha, item.hora, item.nombre, item.convocatoria))
    return ExamenesEsiiab(tuple(unicos))


def _parsear_bloque(html_bloque: str, convocatoria: str) -> list[ExamenEsiiab]:
    resultado: list[ExamenEsiiab] = []
    for nombre_bruto, lista in _BLOQUE.findall(html_bloque):
        nombre = unescape(re.sub(r"<[^>]+>", "", nombre_bruto)).strip()
        if not nombre:
            continue
        campos = {
            clave.strip().casefold(): unescape(valor).strip()
            for clave, valor in _CAMPO.findall(lista)
        }
        fecha = _parsear_fecha(campos.get("día") or campos.get("dia") or "")
        if fecha is None:
            continue
        hora = campos.get("hora") or ""
        centro = campos.get("centro") or ""
        aulas = campos.get("aulas") or ""
        resultado.append(ExamenEsiiab(nombre, fecha, hora, centro, aulas, convocatoria))
    return resultado


def _parsear_fecha(texto: str) -> date | None:
    m = _FECHA.search(texto.strip())
    if not m:
        return None
    return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
