"""Qué cuatrimestre académico está vigente según la fecha de hoy."""

from __future__ import annotations

from datetime import date

from Servidor.Dominio.DominioServices.parser_calendario_esiiab import CalendarioAcademicoEsiiab

_cache: dict[tuple[date, str], int] = {}


def cuatrimestre_actual(
    hoy: date | None = None,
    calendario: CalendarioAcademicoEsiiab | None = None,
) -> int:
    """1 = primer cuatrimestre, 2 = segundo.

    Usa el inicio de clases del segundo cuatrimestre del calendario ESIIAB.
    Si no hay calendario, Sep–Ene → 1 y Feb–Ago → 2.
    """
    momento = hoy or date.today()
    clave_cal = calendario.curso if calendario and calendario.curso else ""
    cache_key = (momento, clave_cal)
    if cache_key in _cache:
        return _cache[cache_key]
    valor = _calcular(momento, calendario)
    _cache[cache_key] = valor
    if len(_cache) > 8:
        _cache.clear()
        _cache[cache_key] = valor
    return valor


def _calcular(momento: date, calendario: CalendarioAcademicoEsiiab | None) -> int:
    if calendario is not None:
        inicios_segundo = [
            fecha.inicio
            for fecha in calendario.fechas
            if fecha.tipo == "inicio_cuatrimestre" and "segundo" in fecha.titulo.casefold()
        ]
        if inicios_segundo:
            inicio_segundo = min(inicios_segundo)
            inicios_primer = [
                fecha.inicio
                for fecha in calendario.fechas
                if fecha.tipo == "inicio_cuatrimestre" and "primer" in fecha.titulo.casefold()
            ]
            if inicios_primer:
                inicio_primer = min(inicios_primer)
                if momento < inicio_primer:
                    return 2 if momento.month < 9 else 1
            return 1 if momento < inicio_segundo else 2
    if momento.month >= 9 or momento.month == 1:
        return 1
    return 2
