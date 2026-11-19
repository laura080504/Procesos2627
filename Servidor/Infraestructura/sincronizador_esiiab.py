"""Mantiene la BBDD de horarios/fichas/calendario/exámenes ESIIAB al día.

Estrategia stale-while-revalidate con caché en proceso: la agenda nunca
espera a la red. Si hay snapshot (BBDD, memoria u offline) se sirve al
instante y el refresco va en segundo plano.
"""

from __future__ import annotations

import logging
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from Servidor.Dominio.DominioServices.normalizar_texto import normalizar_texto
from Servidor.Dominio.DominioServices.parser_calendario_esiiab import (
    CalendarioAcademicoEsiiab,
    parsear_calendario_html,
)
from Servidor.Dominio.DominioServices.parser_examenes_esiiab import ExamenesEsiiab, parsear_examenes_html
from Servidor.Dominio.DominioServices.parser_ficha_esiiab import FichaEsiiab
from Servidor.Dominio.DominioServices.parser_horarios_esiiab import Sesion, parsear_horarios_html
from Servidor.Infraestructura.cliente_horarios_esiiab import (
    ClienteHorariosEsiiab,
    HTML_CALENDARIO_OFFLINE,
    HTML_EXAMENES_OFFLINE,
    HTML_OFFLINE,
)
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_esiiab import RepositorioEsiiab

_log = logging.getLogger(__name__)
_CACHE_PROCESO_SEGUNDOS = 120.0


class SincronizadorEsiiab:
    def __init__(
        self,
        cliente: ClienteHorariosEsiiab,
        repositorio: RepositorioEsiiab,
        ttl_segundos: int = 30 * 60,
        html_offline: Path | None = HTML_OFFLINE,
        html_calendario_offline: Path | None = HTML_CALENDARIO_OFFLINE,
        html_examenes_offline: Path | None = HTML_EXAMENES_OFFLINE,
    ) -> None:
        self.cliente = cliente
        self.repositorio = repositorio
        self.ttl = timedelta(seconds=max(30, ttl_segundos))
        self._html_offline = html_offline
        self._html_calendario_offline = html_calendario_offline
        self._html_examenes_offline = html_examenes_offline
        self._candado = threading.Lock()
        self._candado_calendario = threading.Lock()
        self._candado_examenes = threading.Lock()
        self._refrescando = False
        self._refrescando_calendario = False
        self._refrescando_examenes = False
        self._calentando = False
        self._horario_cache = None
        self._horario_cache_hasta = 0.0
        self._calendario_cache: CalendarioAcademicoEsiiab | None = None
        self._calendario_cache_hasta = 0.0
        self._examenes_cache: ExamenesEsiiab | None = None
        self._examenes_cache_hasta = 0.0
        self._fichas_cache: dict[str, FichaEsiiab] = {}
        self._fichas_cache_nombre: dict[str, FichaEsiiab] = {}
        self._candado_fichas = threading.Lock()
        self._fichas_pendientes: set[str] = set()

    def sesiones(self) -> dict[str, tuple[Sesion, ...]]:
        horario = self.asegurar_horario()
        return horario.sesiones if horario else {}

    def urls_asignaturas(self) -> dict[str, str]:
        horario = self.asegurar_horario()
        return dict(horario.urls) if horario else {}

    def grupos(self) -> tuple[str, ...]:
        horario = self.asegurar_horario()
        return horario.grupos if horario else ()

    def ficha_de(self, nombre: str, codigo: str = "") -> FichaEsiiab | None:
        if codigo:
            guardada = self._ficha_cacheada(codigo, nombre)
            if guardada:
                return guardada
        guardada = self._ficha_cacheada("", nombre)
        if guardada:
            return guardada
        self._lanzar_descarga_fichas([(codigo or nombre, nombre)])
        return None

    def fichas_de(self, asignaturas: list[tuple[str, str]]) -> dict[str, FichaEsiiab]:
        """Solo caché/BBDD: nunca bloquea en red. Las faltantes van en segundo plano."""
        resultado: dict[str, FichaEsiiab] = {}
        pendientes: list[tuple[str, str]] = []
        for codigo, nombre in asignaturas:
            ficha = self._ficha_cacheada(codigo, nombre)
            if ficha and not _ficha_obsoleta(ficha):
                resultado[codigo] = ficha
            else:
                pendientes.append((codigo, nombre))
        if pendientes:
            self._lanzar_descarga_fichas(pendientes)
        return resultado

    def _ficha_cacheada(self, codigo: str, nombre: str = "") -> FichaEsiiab | None:
        if codigo and codigo in self._fichas_cache:
            return self._fichas_cache[codigo]
        if nombre:
            clave = normalizar_texto(nombre)
            if clave in self._fichas_cache_nombre:
                return self._fichas_cache_nombre[clave]
        ficha = None
        if codigo:
            ficha = self.repositorio.obtener_ficha(codigo)
        if ficha is None and nombre:
            ficha = self.repositorio.obtener_ficha_por_nombre(normalizar_texto(nombre))
        if ficha is not None:
            self._guardar_cache_ficha(ficha)
        return ficha

    def _guardar_cache_ficha(self, ficha: FichaEsiiab) -> None:
        if ficha.codigo:
            self._fichas_cache[ficha.codigo] = ficha
        if ficha.nombre:
            self._fichas_cache_nombre[normalizar_texto(ficha.nombre)] = ficha

    def asegurar_horario(self):
        ahora = time.monotonic()
        if self._horario_cache is not None and self._horario_cache.sesiones and ahora < self._horario_cache_hasta:
            return self._horario_cache
        with self._candado:
            ahora = time.monotonic()
            if self._horario_cache is not None and self._horario_cache.sesiones and ahora < self._horario_cache_hasta:
                return self._horario_cache
            existente = self.repositorio.obtener_horario()
            if existente and existente.sesiones:
                self._guardar_cache_horario(existente)
                if not self._esta_fresco_meta(self.repositorio.sincronizado_en()):
                    self._lanzar_refresco()
                return existente
            sembrado = self._sembrar_offline()
            self._lanzar_refresco()
            if sembrado and sembrado.sesiones:
                self._guardar_cache_horario(sembrado)
                return sembrado
            return existente

    def calendario(self) -> CalendarioAcademicoEsiiab | None:
        return self.asegurar_calendario()

    def examenes(self) -> ExamenesEsiiab | None:
        return self.asegurar_examenes()

    def iniciar_en_segundo_plano(self) -> None:
        """Arranque no bloqueante del servidor."""
        threading.Thread(target=self.asegurar_horario, daemon=True, name="esiiab-boot").start()
        threading.Thread(target=self.asegurar_calendario, daemon=True, name="esiiab-cal-boot").start()
        threading.Thread(target=self.asegurar_examenes, daemon=True, name="esiiab-ex-boot").start()

    def asegurar_calendario(self) -> CalendarioAcademicoEsiiab | None:
        ahora = time.monotonic()
        if self._calendario_cache is not None and self._calendario_cache.fechas and ahora < self._calendario_cache_hasta:
            return self._calendario_cache
        with self._candado_calendario:
            ahora = time.monotonic()
            if self._calendario_cache is not None and self._calendario_cache.fechas and ahora < self._calendario_cache_hasta:
                return self._calendario_cache
            existente = self.repositorio.obtener_calendario()
            if existente and existente.fechas:
                self._guardar_cache_calendario(existente)
                if not self._esta_fresco_meta(self.repositorio.calendario_sincronizado_en()):
                    if self.cliente.vivo:
                        self._lanzar_refresco_calendario()
                    else:
                        sembrado = self._sembrar_calendario_offline()
                        if sembrado and sembrado.fechas:
                            self._guardar_cache_calendario(sembrado)
                            return sembrado
                return existente
            sembrado = self._sembrar_calendario_offline()
            self._lanzar_refresco_calendario()
            if sembrado and sembrado.fechas:
                self._guardar_cache_calendario(sembrado)
                return sembrado
            return existente

    def asegurar_examenes(self) -> ExamenesEsiiab | None:
        ahora = time.monotonic()
        if self._examenes_cache is not None and self._examenes_cache.examenes and ahora < self._examenes_cache_hasta:
            return self._examenes_cache
        with self._candado_examenes:
            ahora = time.monotonic()
            if self._examenes_cache is not None and self._examenes_cache.examenes and ahora < self._examenes_cache_hasta:
                return self._examenes_cache
            existente = self.repositorio.obtener_examenes()
            if existente and existente.examenes:
                self._guardar_cache_examenes(existente)
                if not self._esta_fresco_meta(self.repositorio.examenes_sincronizado_en()):
                    if self.cliente.vivo:
                        self._lanzar_refresco_examenes()
                    else:
                        sembrado = self._sembrar_examenes_offline()
                        if sembrado and sembrado.examenes:
                            self._guardar_cache_examenes(sembrado)
                            return sembrado
                return existente
            sembrado = self._sembrar_examenes_offline()
            self._lanzar_refresco_examenes()
            if sembrado and sembrado.examenes:
                self._guardar_cache_examenes(sembrado)
                return sembrado
            return existente

    def _guardar_cache_horario(self, horario) -> None:
        self._horario_cache = horario
        self._horario_cache_hasta = time.monotonic() + _CACHE_PROCESO_SEGUNDOS

    def _guardar_cache_calendario(self, calendario: CalendarioAcademicoEsiiab) -> None:
        self._calendario_cache = calendario
        self._calendario_cache_hasta = time.monotonic() + _CACHE_PROCESO_SEGUNDOS

    def _guardar_cache_examenes(self, examenes: ExamenesEsiiab) -> None:
        self._examenes_cache = examenes
        self._examenes_cache_hasta = time.monotonic() + _CACHE_PROCESO_SEGUNDOS

    def _esta_fresco(self) -> bool:
        if self.repositorio.obtener_horario() is None:
            return False
        return self._esta_fresco_meta(self.repositorio.sincronizado_en())

    def _esta_fresco_meta(self, momento: datetime | None) -> bool:
        if momento is None:
            return False
        ahora = datetime.now(timezone.utc)
        if momento.tzinfo is None:
            momento = momento.replace(tzinfo=timezone.utc)
        return ahora - momento < self.ttl

    def _sembrar_offline(self):
        if not self._html_offline or not self._html_offline.is_file():
            return None
        try:
            horario = parsear_horarios_html(self._html_offline.read_text(encoding="utf-8"))
            if horario.sesiones:
                self.repositorio.guardar_horario(horario)
                _log.info("Horarios ESIIAB sembrados desde HTML offline (%s)", len(horario.sesiones))
            return horario if horario.sesiones else None
        except Exception as error:
            _log.warning("No se pudo sembrar HTML offline: %s", error)
            return None

    def _sembrar_calendario_offline(self) -> CalendarioAcademicoEsiiab | None:
        if not self._html_calendario_offline or not self._html_calendario_offline.is_file():
            return None
        try:
            calendario = parsear_calendario_html(self._html_calendario_offline.read_text(encoding="utf-8"))
            if calendario.fechas:
                self.repositorio.guardar_calendario(calendario)
                _log.info("Calendario ESIIAB sembrado offline (%s fechas)", len(calendario.fechas))
            return calendario if calendario.fechas else None
        except Exception as error:
            _log.warning("No se pudo sembrar calendario offline: %s", error)
            return None

    def _sembrar_examenes_offline(self) -> ExamenesEsiiab | None:
        if not self._html_examenes_offline or not self._html_examenes_offline.is_file():
            return None
        try:
            examenes = parsear_examenes_html(self._html_examenes_offline.read_text(encoding="utf-8"))
            if examenes.examenes:
                self.repositorio.guardar_examenes(examenes)
                _log.info("Exámenes ESIIAB sembrados offline (%s)", len(examenes.examenes))
            return examenes if examenes.examenes else None
        except Exception as error:
            _log.warning("No se pudo sembrar exámenes offline: %s", error)
            return None

    def _lanzar_refresco(self) -> None:
        if self._refrescando or not self.cliente.vivo:
            return
        self._refrescando = True

        def _trabajo() -> None:
            try:
                self._refrescar_ahora()
            finally:
                self._refrescando = False

        threading.Thread(target=_trabajo, daemon=True, name="esiiab-refresh").start()

    def _lanzar_refresco_calendario(self) -> None:
        if self._refrescando_calendario or not self.cliente.vivo:
            return
        self._refrescando_calendario = True

        def _trabajo() -> None:
            try:
                self._refrescar_calendario_ahora()
            finally:
                self._refrescando_calendario = False

        threading.Thread(target=_trabajo, daemon=True, name="esiiab-cal-refresh").start()

    def _lanzar_refresco_examenes(self) -> None:
        if self._refrescando_examenes or not self.cliente.vivo:
            return
        self._refrescando_examenes = True

        def _trabajo() -> None:
            try:
                self._refrescar_examenes_ahora()
            finally:
                self._refrescando_examenes = False

        threading.Thread(target=_trabajo, daemon=True, name="esiiab-ex-refresh").start()

    def _refrescar_ahora(self):
        try:
            self.cliente._caduca_en = 0
            horario = self.cliente._horario_actual()
            if horario and horario.sesiones:
                with self._candado:
                    self.repositorio.guardar_horario(horario)
                    self._guardar_cache_horario(horario)
                self._lanzar_calentamiento_fichas(horario.urls)
                return horario
        except Exception as error:
            _log.warning("No se pudo sincronizar ESIIAB: %s", error)
        return self.repositorio.obtener_horario()

    def _refrescar_calendario_ahora(self) -> CalendarioAcademicoEsiiab | None:
        try:
            calendario = self.cliente.calendario()
            if calendario and calendario.fechas:
                with self._candado_calendario:
                    self.repositorio.guardar_calendario(calendario)
                    self._guardar_cache_calendario(calendario)
                return calendario
        except Exception as error:
            _log.warning("No se pudo sincronizar el calendario ESIIAB: %s", error)
        return self.repositorio.obtener_calendario()

    def _refrescar_examenes_ahora(self) -> ExamenesEsiiab | None:
        try:
            examenes = self.cliente.examenes()
            if examenes and examenes.examenes:
                with self._candado_examenes:
                    self.repositorio.guardar_examenes(examenes)
                    self._guardar_cache_examenes(examenes)
                return examenes
        except Exception as error:
            _log.warning("No se pudieron sincronizar los exámenes ESIIAB: %s", error)
        return self.repositorio.obtener_examenes()

    def _lanzar_descarga_fichas(self, pendientes: list[tuple[str, str]]) -> None:
        if not pendientes or not self.cliente.vivo:
            return
        lote: list[tuple[str, str]] = []
        with self._candado_fichas:
            for codigo, nombre in pendientes:
                clave = codigo or nombre
                if not clave or clave in self._fichas_pendientes:
                    continue
                self._fichas_pendientes.add(clave)
                lote.append((codigo, nombre))
        if not lote:
            return

        def _trabajo() -> None:
            try:
                descargadas = self.cliente.fichas_de(lote)
                for ficha in descargadas.values():
                    self.repositorio.guardar_ficha(ficha)
                    self._guardar_cache_ficha(ficha)
            except Exception as error:
                _log.warning("No se pudieron descargar fichas ESIIAB: %s", error)
            finally:
                with self._candado_fichas:
                    for codigo, nombre in lote:
                        self._fichas_pendientes.discard(codigo or nombre)

        threading.Thread(target=_trabajo, daemon=True, name="esiiab-fichas-faltantes").start()

    def _lanzar_calentamiento_fichas(self, urls: dict[str, str]) -> None:
        if not urls or self._calentando or not self.cliente.vivo:
            return
        self._calentando = True

        def _trabajo() -> None:
            try:
                guardadas = 0
                for nombre_norm, url in urls.items():
                    if self.repositorio.obtener_ficha_por_nombre(nombre_norm):
                        continue
                    ficha = self.cliente._ficha_por_url(url, nombre_fallback=nombre_norm)
                    if ficha:
                        self.repositorio.guardar_ficha(ficha)
                        self._guardar_cache_ficha(ficha)
                        guardadas += 1
                if guardadas:
                    _log.info("Fichas ESIIAB persistidas (%s)", guardadas)
            except Exception as error:
                _log.warning("No se pudieron persistir todas las fichas ESIIAB: %s", error)
            finally:
                self._calentando = False

        threading.Thread(target=_trabajo, daemon=True, name="esiiab-sync-fichas").start()


def _ficha_obsoleta(ficha: FichaEsiiab) -> bool:
    """Detecta el bug viejo que duplicaba el bloque entero de tutorías en ambos cuatris.

    Un profesor puede tener las mismas franjas en 1.º y 2.º de verdad (p. ej. Sahori
    en Sistemas Distribuidos); eso no invalida la ficha. Solo es obsoleta si el
    mapa completo primer==segundo y hay franjas (copia wholesale del parser antiguo).
    """
    if not ficha.profesores:
        return True
    mapa_primer = tuple((normalizar_texto(p.nombre), p.tutorias_primer) for p in ficha.profesores)
    mapa_segundo = tuple((normalizar_texto(p.nombre), p.tutorias_segundo) for p in ficha.profesores)
    hay_franjas = any(p.tutorias_primer or p.tutorias_segundo for p in ficha.profesores)
    return hay_franjas and mapa_primer == mapa_segundo
