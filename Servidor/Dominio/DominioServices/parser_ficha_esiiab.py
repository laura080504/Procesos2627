"""Parser de la ficha pública de una asignatura en esiiab.uclm.es/asignatura/..."""

from __future__ import annotations

import re
from dataclasses import dataclass
from html import unescape

from Servidor.Dominio.DominioServices.normalizar_texto import normalizar_texto

_RE_CODIGO = re.compile(r"C[oó]digo\s+Asignatura:\s*(\d+)", re.IGNORECASE)
_RE_PROFESOR = re.compile(
    r'<a[^>]*href="(https://esiiab\.uclm\.es/personal/[^"]+/)"[^>]*class="[^"]*penci-personal-name[^"]*"[^>]*>\s*([^<]+?)\s*</a>'
    r'|<a[^>]*class="[^"]*penci-personal-name[^"]*"[^>]*href="(https://esiiab\.uclm\.es/personal/[^"]+/)"[^>]*>\s*([^<]+?)\s*</a>',
    re.IGNORECASE,
)
_RE_BLOQUE_TUTORIAS = re.compile(
    r'<h6 class="[^"]*nombre-profe-tuto[^"]*"[^>]*>([^<]+)</h6>([\s\S]*?)(?=<h6 class="[^"]*nombre-profe-tuto|</div>\s*</div>\s*</div>|$)',
    re.IGNORECASE,
)
_RE_DIA = re.compile(
    r"(Lunes|Martes|Mi[eé]rcoles|Jueves|Viernes|S[aá]bado|Domingo)\s*:\s*\d{1,2}:\d{2}\s*[-–—]\s*\d{1,2}:\d{2}",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ProfesorEsiiab:
    nombre: str
    url: str
    tutorias: tuple[str, ...] = ()


@dataclass(frozen=True)
class FichaEsiiab:
    codigo: str
    nombre: str
    url: str
    profesores: tuple[ProfesorEsiiab, ...]


def parsear_ficha_html(html: str, url: str = "") -> FichaEsiiab:
    codigo = _codigo_de(html)
    nombre = _nombre_de(html)
    profesores = _profesores_de(html)
    tutorias = _tutorias_por_profesor(html)
    enriquecidos = []
    for profesor in profesores:
        clave = normalizar_texto(profesor.nombre)
        enriquecidos.append(
            ProfesorEsiiab(profesor.nombre, profesor.url, tutorias.get(clave, ()))
        )
    if not enriquecidos and tutorias:
        enriquecidos = [
            ProfesorEsiiab(nombre=nombre_prof, url="", tutorias=franjas)
            for nombre_prof, franjas in (
                (_nombre_desde_clave(clave), valores) for clave, valores in tutorias.items()
            )
        ]
    return FichaEsiiab(codigo, nombre, url, tuple(enriquecidos))


def _codigo_de(html: str) -> str:
    match = _RE_CODIGO.search(html)
    return match.group(1) if match else ""


def _nombre_de(html: str) -> str:
    for patron in (
        r"<h1[^>]*>\s*([^<]+?)\s*</h1>",
        r'property="og:title"\s+content="([^"|]+)',
    ):
        match = re.search(patron, html, re.IGNORECASE)
        if match:
            return unescape(match.group(1)).strip()
    return ""


def _profesores_de(html: str) -> list[ProfesorEsiiab]:
    vistos: set[str] = set()
    resultado: list[ProfesorEsiiab] = []
    for match in _RE_PROFESOR.finditer(html):
        url = match.group(1) or match.group(3) or ""
        nombre = unescape((match.group(2) or match.group(4) or "").strip())
        clave = normalizar_texto(nombre)
        if not nombre or clave in vistos:
            continue
        vistos.add(clave)
        resultado.append(ProfesorEsiiab(nombre, url))
    return resultado


def _tutorias_por_profesor(html: str) -> dict[str, tuple[str, ...]]:
    """Une las franjas de ambos cuatrimestres por nombre de profesor."""
    acumulado: dict[str, list[str]] = {}
    for bloque in _RE_BLOQUE_TUTORIAS.finditer(html):
        clave = normalizar_texto(unescape(bloque.group(1)))
        if not clave:
            continue
        cuerpo = unescape(bloque.group(2)).replace("–", "-").replace("—", "-")
        cuerpo = re.sub(r"<br\s*/?>", "\n", cuerpo, flags=re.IGNORECASE)
        franjas = [match.group(0).strip() for match in _RE_DIA.finditer(cuerpo)]
        lista = acumulado.setdefault(clave, [])
        for franja in franjas:
            if franja not in lista:
                lista.append(franja)
    return {clave: tuple(valores) for clave, valores in acumulado.items()}


def _nombre_desde_clave(clave: str) -> str:
    return clave.upper()
