"""Cliente HTTP de horarios y fichas públicas de la ESIIAB.

Consulta https://esiiab.uclm.es/horarios/ y, bajo demanda, las fichas
/asignatura/... (profesores y tutorías). Cachea en memoria durante un TTL.
Si la red falla, reutiliza la última respuesta o el HTML offline embebido.
"""

from __future__ import annotations

import logging
import threading
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from Servidor.Dominio.DominioServices.normalizar_texto import normalizar_texto
from Servidor.Dominio.DominioServices.parser_calendario_esiiab import (
    CalendarioAcademicoEsiiab,
    parsear_calendario_html,
)
from Servidor.Dominio.DominioServices.parser_examenes_esiiab import ExamenesEsiiab, parsear_examenes_html
from Servidor.Dominio.DominioServices.parser_ficha_esiiab import FichaEsiiab, parsear_ficha_html
from Servidor.Dominio.DominioServices.parser_horarios_esiiab import (
    HorarioPublicoEsiiab,
    Sesion,
    parsear_horarios_html,
)

URL_HORARIOS_ESIIAB = "https://esiiab.uclm.es/horarios/"
URL_CALENDARIO_ESIIAB = "https://esiiab.uclm.es/calendario-academico/"
URL_EXAMENES_ESIIAB = "https://esiiab.uclm.es/examenes/"
TTL_POR_DEFECTO_SEGUNDOS = 5 * 60
_FIXTURES = Path(__file__).resolve().parents[2] / "Pruebas" / "PruebasUseCase" / "fixtures"
HTML_OFFLINE = _FIXTURES / "horarios_esiiab_offline.html"
HTML_CALENDARIO_OFFLINE = _FIXTURES / "calendario_academico_esiiab_offline.html"
HTML_EXAMENES_OFFLINE = _FIXTURES / "examenes_esiiab_offline.html"

_log = logging.getLogger(__name__)


class ClienteHorariosEsiiab:
    def __init__(
        self,
        url: str = URL_HORARIOS_ESIIAB,
        ttl_segundos: int = TTL_POR_DEFECTO_SEGUNDOS,
        vivo: bool = True,
        descargar: Callable[[str], str] | None = None,
        html_offline: Path | None = HTML_OFFLINE,
        url_calendario: str = URL_CALENDARIO_ESIIAB,
        url_examenes: str = URL_EXAMENES_ESIIAB,
        html_calendario_offline: Path | None = HTML_CALENDARIO_OFFLINE,
        html_examenes_offline: Path | None = HTML_EXAMENES_OFFLINE,
    ) -> None:
        self.url = url
        self.url_calendario = url_calendario
        self.url_examenes = url_examenes
        self.ttl_segundos = max(30, ttl_segundos)
        self.vivo = vivo
        self._descargar = descargar or _descargar_html
        self._html_offline = html_offline
        self._html_calendario_offline = html_calendario_offline
        self._html_examenes_offline = html_examenes_offline
        self._candado = threading.Lock()
        self._horario: HorarioPublicoEsiiab | None = None
        self._caduca_en = 0.0
        self._fichas: dict[str, tuple[float, FichaEsiiab]] = {}

    def sesiones(self) -> dict[str, tuple[Sesion, ...]]:
        return self._horario_actual().sesiones

    def urls_asignaturas(self) -> dict[str, str]:
        return self._horario_actual().urls

    def grupos(self) -> tuple[str, ...]:
        return self._horario_actual().grupos

    def ficha_de(self, nombre: str, codigo: str = "") -> FichaEsiiab | None:
        horario = self._horario_actual()
        clave = normalizar_texto(nombre)
        url = horario.urls.get(clave)
        if not url:
            return None
        return self._ficha_por_url(url, nombre_fallback=nombre, codigo_fallback=codigo)

    def fichas_de(self, asignaturas: list[tuple[str, str]]) -> dict[str, FichaEsiiab]:
        """asignaturas = [(codigo, nombre), ...]. Devuelve fichas por código."""
        horario = self._horario_actual()
        pendientes: list[tuple[str, str, str]] = []
        resultado: dict[str, FichaEsiiab] = {}
        for codigo, nombre in asignaturas:
            url = horario.urls.get(normalizar_texto(nombre))
            if not url:
                continue
            cacheada = self._ficha_cacheada(url)
            if cacheada is not None:
                resultado[codigo] = cacheada
            else:
                pendientes.append((codigo, nombre, url))
        if not pendientes:
            return resultado
        with ThreadPoolExecutor(max_workers=min(6, len(pendientes))) as pool:
            futuros = {
                pool.submit(self._ficha_por_url, url, nombre, codigo): codigo
                for codigo, nombre, url in pendientes
            }
            for futuro in as_completed(futuros):
                codigo = futuros[futuro]
                try:
                    ficha = futuro.result()
                except Exception as error:
                    _log.warning("No se pudo leer la ficha de %s: %s", codigo, error)
                    continue
                if ficha is not None:
                    resultado[codigo] = ficha
        return resultado

    def _horario_actual(self) -> HorarioPublicoEsiiab:
        ahora = time.monotonic()
        with self._candado:
            if self._horario is not None and ahora < self._caduca_en:
                return self._horario
            try:
                html = self._html_horarios()
                horario = parsear_horarios_html(html)
                if not horario.sesiones:
                    raise ValueError("La página de horarios no contiene tablas reconocibles")
                self._horario = horario
                self._caduca_en = ahora + self.ttl_segundos
                _log.info(
                    "Horarios ESIIAB actualizados (%s asignaturas, %s grupos, %s fichas)",
                    len(horario.sesiones),
                    len(horario.grupos),
                    len(horario.urls),
                )
                return horario
            except Exception as error:
                _log.warning("No se pudieron refrescar los horarios ESIIAB: %s", error)
                if self._horario is not None:
                    return self._horario
                return HorarioPublicoEsiiab({}, {}, ())

    def calendario(self) -> CalendarioAcademicoEsiiab:
        html = self._html_de(self.url_calendario, self._html_calendario_offline, "calendario académico")
        return parsear_calendario_html(html)

    def examenes(self) -> ExamenesEsiiab:
        html = self._html_de(self.url_examenes, self._html_examenes_offline, "exámenes")
        return parsear_examenes_html(html)

    def _html_horarios(self) -> str:
        return self._html_de(self.url, self._html_offline, "horarios")

    def _html_de(self, url: str, offline: Path | None, etiqueta: str) -> str:
        if self.vivo:
            return self._descargar(url)
        if offline and offline.is_file():
            return offline.read_text(encoding="utf-8")
        raise FileNotFoundError(f"No hay HTML offline de {etiqueta} ESIIAB")

    def _leer_offline(self) -> str:
        return self._html_de(self.url, self._html_offline, "horarios")

    def _ficha_cacheada(self, url: str) -> FichaEsiiab | None:
        with self._candado:
            entrada = self._fichas.get(url)
            if entrada is None:
                return None
            caduca_en, ficha = entrada
            if time.monotonic() < caduca_en:
                return ficha
            return None

    def _ficha_por_url(
        self,
        url: str,
        nombre_fallback: str = "",
        codigo_fallback: str = "",
    ) -> FichaEsiiab | None:
        cacheada = self._ficha_cacheada(url)
        if cacheada is not None:
            return cacheada
        if not self.vivo:
            return FichaEsiiab(codigo_fallback, nombre_fallback, url, ())
        try:
            html = self._descargar(url)
            ficha = parsear_ficha_html(html, url=url)
            if not ficha.codigo and codigo_fallback:
                ficha = FichaEsiiab(codigo_fallback, ficha.nombre or nombre_fallback, url, ficha.profesores)
            elif not ficha.nombre and nombre_fallback:
                ficha = FichaEsiiab(ficha.codigo or codigo_fallback, nombre_fallback, url, ficha.profesores)
            with self._candado:
                self._fichas[url] = (time.monotonic() + self.ttl_segundos, ficha)
            return ficha
        except Exception as error:
            _log.warning("Fallo al descargar ficha %s: %s", url, error)
            return None


def _descargar_html(url: str) -> str:
    peticion = Request(
        url,
        headers={
            "User-Agent": "Procesos2627/1.0 (+horarios y fichas ESIIAB)",
            "Accept": "text/html,application/xhtml+xml",
        },
        method="GET",
    )
    try:
        with urlopen(peticion, timeout=20) as respuesta:
            bruto = respuesta.read()
            charset = respuesta.headers.get_content_charset() or "utf-8"
        return bruto.decode(charset, errors="replace")
    except (HTTPError, URLError, TimeoutError) as error:
        raise error
