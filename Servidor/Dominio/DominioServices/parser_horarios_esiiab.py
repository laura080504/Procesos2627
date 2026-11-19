"""Parser del HTML público de https://esiiab.uclm.es/horarios/.

Incluye todos los cursos, grupos (A/B/C/I) e intensificaciones/optativas
publicados en la página. Cada sesión lleva grupo y cuatrimestre de su tabla.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import urljoin

from Servidor.Dominio.DominioServices.normalizar_texto import normalizar_texto

# dia, inicio, fin, tipo, aula, grupo, cuatrimestre (1|2)
Sesion = tuple[int, str, str, str, str, str, int]
BASE_ESIIAB = "https://esiiab.uclm.es"

_DIAS = {"lunes": 0, "martes": 1, "miercoles": 2, "jueves": 3, "viernes": 4}
_RE_GRUPO = re.compile(
    r"(?P<curso>\d)º\s+GRUPO\s+(?P<grupo>[^-\n<]+?)\s*-\s*(?P<semestre>\d)\s+Semestre",
    re.IGNORECASE,
)
# Tablas únicas sin desdoble A/B, p.ej. "3º Aspectos Prof. Inf. - 2 Semestre".
_RE_ESPECIAL = re.compile(
    r"(?P<curso>\d)º\s+(?P<grupo>(?!GRUPO\b)[^-\n<]+?)\s*-\s*(?P<semestre>\d)\s+Semestre",
    re.IGNORECASE,
)
_RE_HORA = re.compile(r"(\d{1,2}):(\d{2})")
_RE_ENLACE = re.compile(
    r'href="(/asignatura/[^"]+)"[^>]*>\s*([^<]+?)\s*</a>',
    re.IGNORECASE,
)
# Aulas ESIIAB que implican prácticas (no teoría magistral).
_MARCAS_PRACTICAS = ("softw", "hw", "elect", "lab", "multiusos", "seminario")
_RE_AULA_CERO = re.compile(r"aula\s*0\.\d", re.IGNORECASE)
# Marcador interno: tabla sin cabecera GRUPO A/B; 1ª franja = A, 2ª = B…
_GRUPO_POR_FILA = "#FILA"
_LETRAS_FILA = ("A", "B", "C", "I")
_TARDE_DESDE_MINUTOS = 16 * 60


@dataclass(frozen=True)
class HorarioPublicoEsiiab:
    sesiones: dict[str, tuple[Sesion, ...]]
    urls: dict[str, str]
    grupos: tuple[str, ...]


def parsear_horarios_html(html: str, base: str = BASE_ESIIAB) -> HorarioPublicoEsiiab:
    """Devuelve sesiones (con grupo y cuatrimestre), URLs de ficha y listado de grupos."""
    bloques = _bloques_horario(html)
    acumulado: dict[str, list[Sesion]] = {}
    urls: dict[str, str] = {}
    grupos_vistos: list[str] = []
    for cabecera, tabla in bloques:
        grupo, cuatrimestre = _grupo_y_cuatrimestre(cabecera)
        if grupo is None or not cuatrimestre:
            continue
        if grupo and grupo != _GRUPO_POR_FILA and grupo not in grupos_vistos:
            grupos_vistos.append(grupo)
        elif grupo == _GRUPO_POR_FILA:
            for letra in _LETRAS_FILA[:2]:
                if letra not in grupos_vistos:
                    grupos_vistos.append(letra)
        for nombre, sesion, enlace in _sesiones_de_tabla(tabla, grupo, cuatrimestre):
            clave = normalizar_texto(nombre)
            if not clave:
                continue
            lista = acumulado.setdefault(clave, [])
            if sesion not in lista:
                lista.append(sesion)
            if enlace and clave not in urls:
                urls[clave] = urljoin(base, enlace)
    for enlace, nombre in _RE_ENLACE.findall(html):
        clave = normalizar_texto(nombre)
        if clave and clave not in urls:
            urls[clave] = urljoin(base, enlace)
    return HorarioPublicoEsiiab(
        {
            nombre: tuple(
                sorted(
                    _ajustar_tipos_practicas(sesiones),
                    key=lambda s: (s[6], s[5], s[0], s[1], s[2], s[3], s[4]),
                )
            )
            for nombre, sesiones in acumulado.items()
        },
        urls,
        tuple(grupos_vistos),
    )


def _grupo_y_cuatrimestre(cabecera: str) -> tuple[str | None, int]:
    texto = re.sub(r"\s+", " ", cabecera).strip()
    match = _RE_GRUPO.search(texto)
    especial = False
    if not match:
        match = _RE_ESPECIAL.search(texto)
        especial = True
    if not match:
        return None, 0
    cuatrimestre = int(match.group("semestre"))
    if especial:
        return _GRUPO_POR_FILA, cuatrimestre
    crudo = re.sub(r"\(BILING[ÜU]E\)", "", match.group("grupo"), flags=re.IGNORECASE).strip()
    crudo = re.sub(r"\(\d{1,3}\)", "", crudo).strip()
    letra = re.match(r"^([A-Za-z])\b", crudo)
    if letra and letra.group(1).upper() in {"A", "B", "C", "I"}:
        return letra.group(1).upper(), cuatrimestre
    etiqueta = re.sub(r"\s+", " ", crudo).strip(" .") or None
    return etiqueta, cuatrimestre


def _bloques_horario(html: str) -> list[tuple[str, str]]:
    bloques: list[tuple[str, str]] = []
    for match in re.finditer(r"<table[^>]*tableHorario[^>]*>[\s\S]*?</table>", html, re.IGNORECASE):
        previa = html[max(0, match.start() - 800) : match.start()]
        cabeceras = re.findall(
            r"\dº\s+(?:GRUPO\s+)?[\s\S]{0,140}?Semestre[\s\S]{0,80}?20\d{2}\s*-\s*20\d{2}",
            previa,
            re.IGNORECASE,
        )
        cabecera = re.sub(r"<[^>]+>", " ", cabeceras[-1] if cabeceras else "")
        bloques.append((cabecera, match.group(0)))
    return bloques


def _sesiones_de_tabla(
    tabla_html: str,
    grupo: str,
    cuatrimestre: int,
) -> list[tuple[str, Sesion, str]]:
    filas = _TablaHorario().leer(tabla_html)
    if not filas:
        return []
    cabecera = [normalizar_texto(celda) for celda in filas[0]]
    indices_dia = {indice: _DIAS[texto] for indice, texto in enumerate(cabecera) if texto in _DIAS}
    resultado: list[tuple[str, Sesion, str]] = []
    indice_franja = 0
    for fila in filas[1:]:
        if not fila:
            continue
        inicio, fin = _horas_de(fila[0])
        if not inicio:
            continue
        grupo_fila = grupo
        if grupo == _GRUPO_POR_FILA:
            grupo_fila = (
                _LETRAS_FILA[indice_franja]
                if indice_franja < len(_LETRAS_FILA)
                else f"F{indice_franja + 1}"
            )
            indice_franja += 1
        for indice, dia in indices_dia.items():
            if indice >= len(fila):
                continue
            nombre, aula, enlace = _celda_asignatura(fila[indice])
            if not nombre:
                continue
            resultado.append(
                (
                    nombre,
                    (dia, inicio, fin, _tipo_de(aula), aula, grupo_fila, cuatrimestre),
                    enlace,
                )
            )
    return resultado


def _horas_de(texto: str) -> tuple[str, str]:
    horas = _RE_HORA.findall(texto)
    if len(horas) < 2:
        return "", ""
    return _hora(horas[0]), _hora(horas[1])


def _hora(partes: tuple[str, str]) -> str:
    return f"{int(partes[0]):02d}:{partes[1]}"


def _celda_asignatura(celda: str) -> tuple[str, str, str]:
    enlace_match = re.search(r'href="(/asignatura/[^"]+)"', celda)
    enlace = enlace_match.group(1) if enlace_match else ""
    lineas = [linea.strip() for linea in re.split(r"[\n\r]+", celda) if linea.strip()]
    if not lineas:
        return "", "", enlace
    return lineas[0], (lineas[1] if len(lineas) > 1 else ""), enlace


def _tipo_de(aula: str) -> str:
    """Clasifica según el local ESIIAB: lab/SOFTW/0.x/multiusos → prácticas."""
    texto = normalizar_texto(aula)
    if any(marca in texto for marca in _MARCAS_PRACTICAS):
        return "practicas"
    if _RE_AULA_CERO.search(aula or ""):
        return "practicas"
    return "teoria"


def _es_aula_generica(aula: str) -> bool:
    texto = normalizar_texto(aula)
    if not texto.startswith("aula"):
        return False
    if _RE_AULA_CERO.search(aula or ""):
        return False
    if any(marca in texto for marca in _MARCAS_PRACTICAS):
        return False
    return True


def _minutos_de(hora: str) -> int:
    horas, minutos = hora.split(":")
    return int(horas) * 60 + int(minutos)


def _ajustar_tipos_practicas(sesiones: list[Sesion]) -> list[Sesion]:
    """En intensificaciones todo va a AULA: la tarde (≥16:00) es práctica.

    Si el grupo ya tiene alguna sesión en lab/SOFTW, no se toca (el aula basta).
    """
    por_clave: dict[tuple[str, int], list[Sesion]] = {}
    for sesion in sesiones:
        por_clave.setdefault((sesion[5], sesion[6]), []).append(sesion)
    resultado: list[Sesion] = []
    for bloque in por_clave.values():
        if any(sesion[3] == "practicas" for sesion in bloque):
            resultado.extend(bloque)
            continue
        for dia, inicio, fin, tipo, aula, grupo, cuatrimestre in bloque:
            if (
                tipo == "teoria"
                and _es_aula_generica(aula)
                and _minutos_de(inicio) >= _TARDE_DESDE_MINUTOS
            ):
                tipo = "practicas"
            resultado.append((dia, inicio, fin, tipo, aula, grupo, cuatrimestre))
    return resultado


class _TablaHorario(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._filas: list[list[str]] = []
        self._fila: list[str] | None = None
        self._celda: list[str] | None = None
        self._capturando = False

    def leer(self, html: str) -> list[list[str]]:
        self.feed(html)
        self.close()
        return self._filas

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "tr":
            self._fila = []
        elif tag == "td" and self._fila is not None:
            self._celda = []
            self._capturando = True
        elif tag == "br" and self._celda is not None:
            self._celda.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag == "td" and self._fila is not None and self._celda is not None:
            self._fila.append("".join(self._celda).strip())
            self._celda = None
            self._capturando = False
        elif tag == "tr" and self._fila is not None:
            self._filas.append(self._fila)
            self._fila = None

    def handle_data(self, data: str) -> None:
        if self._capturando and self._celda is not None:
            self._celda.append(data)
