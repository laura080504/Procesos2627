from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from Servidor.Dominio.DominioServices.parser_calendario_esiiab import CalendarioAcademicoEsiiab
from Servidor.Dominio.DominioServices.parser_examenes_esiiab import ExamenesEsiiab
from Servidor.Dominio.DominioServices.parser_ficha_esiiab import FichaEsiiab
from Servidor.Dominio.DominioServices.parser_horarios_esiiab import HorarioPublicoEsiiab, Sesion


class RepositorioEsiiab(ABC):
    @abstractmethod
    def guardar_horario(self, horario: HorarioPublicoEsiiab, sincronizado_en: datetime | None = None) -> None: ...

    @abstractmethod
    def obtener_horario(self) -> HorarioPublicoEsiiab | None: ...

    @abstractmethod
    def sincronizado_en(self) -> datetime | None: ...

    @abstractmethod
    def guardar_ficha(self, ficha: FichaEsiiab) -> None: ...

    @abstractmethod
    def obtener_ficha(self, codigo: str) -> FichaEsiiab | None: ...

    @abstractmethod
    def obtener_ficha_por_nombre(self, nombre_normalizado: str) -> FichaEsiiab | None: ...

    @abstractmethod
    def guardar_calendario(self, calendario: CalendarioAcademicoEsiiab, sincronizado_en: datetime | None = None) -> None: ...

    @abstractmethod
    def obtener_calendario(self) -> CalendarioAcademicoEsiiab | None: ...

    @abstractmethod
    def calendario_sincronizado_en(self) -> datetime | None: ...

    @abstractmethod
    def guardar_examenes(self, examenes: ExamenesEsiiab, sincronizado_en: datetime | None = None) -> None: ...

    @abstractmethod
    def obtener_examenes(self) -> ExamenesEsiiab | None: ...

    @abstractmethod
    def examenes_sincronizado_en(self) -> datetime | None: ...
