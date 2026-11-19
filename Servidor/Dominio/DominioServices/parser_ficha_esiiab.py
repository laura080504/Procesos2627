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
_RE_SEGUNDO = re.compile(r"Segundo\s+[Cc]uatrimestre", re.IGNORECASE)
_RE_PRIMER = re.compile(r"Primer\s+[Cc]uatrimestre", re.IGNORECASE)


@dataclass(frozen=True)
class ProfesorEsiiab:
    nombre: str
    url: str
    tutorias_primer: tuple[str, ...] = ()
    tutorias_segundo: tuple[str, ...] = ()

    @property
    def tutorias(self) -> tuple[str, ...]:
        """Compat: todas las franjas (útil en tests legacy). Preferir tutorias_de()."""
        vistos: list[str] = []
        for franja in (*self.tutorias_primer, *self.tutorias_segundo):
            if franja not in vistos:
                vistos.append(franja)
        return tuple(vistos)

    def tutorias_de(self, cuatrimestre: int) -> tuple[str, ...]:
        if cuatrimestre == 2:
            return self.tutorias_segundo
        return self.tutorias_primer


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
    primer, segundo = _tutorias_por_cuatrimestre(html)
    enriquecidos = []
    for profesor in profesores:
        clave = normalizar_texto(profesor.nombre)
        enriquecidos.append(
            ProfesorEsiiab(
                profesor.nombre,
                profesor.url,
                primer.get(clave, ()),
                segundo.get(clave, ()),
            )
        )
    if not enriquecidos and (primer or segundo):
        claves = set(primer) | set(segundo)
        enriquecidos = [
            ProfesorEsiiab(
                _nombre_desde_clave(clave),
                "",
                primer.get(clave, ()),
                segundo.get(clave, ()),
            )
            for clave in claves
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


def _tutorias_por_cuatrimestre(html: str) -> tuple[dict[str, tuple[str, ...]], dict[str, tuple[str, ...]]]:
    """Separa las franjas del primer y del segundo cuatrimestre."""
    corte = _RE_SEGUNDO.search(html)
    if corte:
        html_primer = html[: corte.start()]
        html_segundo = html[corte.start() :]
        # Si no hay cabecera de primer cuatri, lo anterior al segundo sigue siendo el primero.
        return _tutorias_en_bloque(html_primer), _tutorias_en_bloque(html_segundo)

    if _RE_PRIMER.search(html):
        return _tutorias_en_bloque(html), {}
    # Sin marcas de cuatrimestre: se asumen vigentes para ambos hasta que haya ficha completa.
    unicas = _tutorias_en_bloque(html)
    return unicas, unicas


def _tutorias_en_bloque(html: str) -> dict[str, tuple[str, ...]]:
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
