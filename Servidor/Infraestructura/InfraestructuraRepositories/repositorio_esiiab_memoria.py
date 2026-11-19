from __future__ import annotations

from datetime import datetime, timezone

from Servidor.Dominio.DominioServices.normalizar_texto import normalizar_texto
from Servidor.Dominio.DominioServices.parser_ficha_esiiab import FichaEsiiab
from Servidor.Dominio.DominioServices.parser_horarios_esiiab import HorarioPublicoEsiiab, Sesion
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_esiiab import RepositorioEsiiab


class RepositorioEsiiabMemoria(RepositorioEsiiab):
    def __init__(self) -> None:
        self._horario: HorarioPublicoEsiiab | None = None
        self._sincronizado_en: datetime | None = None
        self._fichas_codigo: dict[str, FichaEsiiab] = {}
        self._fichas_nombre: dict[str, FichaEsiiab] = {}

    def guardar_horario(self, horario: HorarioPublicoEsiiab, sincronizado_en: datetime | None = None) -> None:
        self._horario = horario
        self._sincronizado_en = sincronizado_en or datetime.now(timezone.utc)

    def obtener_horario(self) -> HorarioPublicoEsiiab | None:
        return self._horario

    def sincronizado_en(self) -> datetime | None:
        return self._sincronizado_en

    def guardar_ficha(self, ficha: FichaEsiiab) -> None:
        if ficha.codigo:
            self._fichas_codigo[ficha.codigo] = ficha
        if ficha.nombre:
            self._fichas_nombre[normalizar_texto(ficha.nombre)] = ficha

    def obtener_ficha(self, codigo: str) -> FichaEsiiab | None:
        return self._fichas_codigo.get(codigo)

    def obtener_ficha_por_nombre(self, nombre_normalizado: str) -> FichaEsiiab | None:
        return self._fichas_nombre.get(nombre_normalizado)
