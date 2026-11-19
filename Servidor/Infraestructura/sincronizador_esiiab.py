"""Mantiene la BBDD de horarios/fichas ESIIAB al día.

Estrategia stale-while-revalidate: si ya hay datos en BBDD se sirven al
instante y el refresco de la web va en segundo plano. Así la agenda no
espera a ESIIAB en cada petición.
"""

from __future__ import annotations

import logging
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path

from Servidor.Dominio.DominioServices.normalizar_texto import normalizar_texto
from Servidor.Dominio.DominioServices.parser_ficha_esiiab import FichaEsiiab
from Servidor.Dominio.DominioServices.parser_horarios_esiiab import Sesion, parsear_horarios_html
from Servidor.Infraestructura.cliente_horarios_esiiab import ClienteHorariosEsiiab, HTML_OFFLINE
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_esiiab import RepositorioEsiiab

_log = logging.getLogger(__name__)


class SincronizadorEsiiab:
    def __init__(
        self,
        cliente: ClienteHorariosEsiiab,
        repositorio: RepositorioEsiiab,
        ttl_segundos: int = 5 * 60,
        html_offline: Path | None = HTML_OFFLINE,
    ) -> None:
        self.cliente = cliente
        self.repositorio = repositorio
        self.ttl = timedelta(seconds=max(30, ttl_segundos))
        self._html_offline = html_offline
        self._candado = threading.Lock()
        self._refrescando = False
        self._calentando = False

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
        self.asegurar_horario()
        if codigo:
            guardada = self.repositorio.obtener_ficha(codigo)
            if guardada:
                return guardada
        guardada = self.repositorio.obtener_ficha_por_nombre(normalizar_texto(nombre))
        if guardada:
            return guardada
        self._lanzar_descarga_fichas([(codigo or nombre, nombre)])
        return None

    def fichas_de(self, asignaturas: list[tuple[str, str]]) -> dict[str, FichaEsiiab]:
        """Solo lee BBDD; las faltantes se descargan en segundo plano."""
        self.asegurar_horario()
        resultado: dict[str, FichaEsiiab] = {}
        pendientes: list[tuple[str, str]] = []
        for codigo, nombre in asignaturas:
            ficha = self.repositorio.obtener_ficha(codigo) or self.repositorio.obtener_ficha_por_nombre(
                normalizar_texto(nombre)
            )
            if ficha:
                resultado[codigo] = ficha
            else:
                pendientes.append((codigo, nombre))
        if pendientes:
            self._lanzar_descarga_fichas(pendientes)
        return resultado

    def asegurar_horario(self):
        with self._candado:
            existente = self.repositorio.obtener_horario()
            if existente and existente.sesiones:
                if not self._esta_fresco():
                    self._lanzar_refresco()
                return existente
            sembrado = self._sembrar_offline()
            if sembrado and sembrado.sesiones:
                self._lanzar_refresco()
                return sembrado
        # Primera carga sin snapshot: una sola sync bloqueante.
        return self._refrescar_ahora()

    def iniciar_en_segundo_plano(self) -> None:
        """Arranque no bloqueante del servidor."""
        threading.Thread(target=self.asegurar_horario, daemon=True, name="esiiab-boot").start()

    def _esta_fresco(self) -> bool:
        momento = self.repositorio.sincronizado_en()
        if momento is None or self.repositorio.obtener_horario() is None:
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

    def _refrescar_ahora(self):
        try:
            self.cliente._caduca_en = 0
            horario = self.cliente._horario_actual()
            if horario and horario.sesiones:
                with self._candado:
                    self.repositorio.guardar_horario(horario)
                self._lanzar_calentamiento_fichas(horario.urls)
                return horario
        except Exception as error:
            _log.warning("No se pudo sincronizar ESIIAB: %s", error)
        return self.repositorio.obtener_horario()

    def _lanzar_descarga_fichas(self, pendientes: list[tuple[str, str]]) -> None:
        if not pendientes or not self.cliente.vivo:
            return

        def _trabajo() -> None:
            try:
                descargadas = self.cliente.fichas_de(pendientes)
                for ficha in descargadas.values():
                    self.repositorio.guardar_ficha(ficha)
            except Exception as error:
                _log.warning("No se pudieron descargar fichas ESIIAB: %s", error)

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
                        guardadas += 1
                if guardadas:
                    _log.info("Fichas ESIIAB persistidas (%s)", guardadas)
            except Exception as error:
                _log.warning("No se pudieron persistir todas las fichas ESIIAB: %s", error)
            finally:
                self._calentando = False

        threading.Thread(target=_trabajo, daemon=True, name="esiiab-sync-fichas").start()
