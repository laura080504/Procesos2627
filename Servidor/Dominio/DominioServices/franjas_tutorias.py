"""Convierte franjas textuales de tutorías ESIIAB en bloques de horario."""

from __future__ import annotations

import re

from Servidor.Dominio.DominioServices.horario_asignatura import FranjaHorario

_DIAS = {
    "lunes": 1,
    "martes": 2,
    "miercoles": 3,
    "miércoles": 3,
    "jueves": 4,
    "viernes": 5,
    "sabado": 6,
    "sábado": 6,
    "domingo": 7,
}
_RE_FRANJA = re.compile(
    r"(Lunes|Martes|Mi[eé]rcoles|Jueves|Viernes|S[aá]bado|Domingo)\s*:\s*"
    r"(\d{1,2}:\d{2})\s*[-–—]\s*(\d{1,2}:\d{2})",
    re.IGNORECASE,
)


def franjas_tutorias_de(
    codigo: str,
    nombre: str,
    nombre_ingles: str,
    lineas: tuple[str, ...] | list[str],
    cuatrimestre: int = 0,
) -> list[FranjaHorario]:
    resultado: list[FranjaHorario] = []
    vistos: set[tuple[int, str, str]] = set()
    for linea in lineas:
        for match in _RE_FRANJA.finditer(linea or ""):
            dia = _DIAS.get(match.group(1).lower().replace("é", "e").replace("á", "a"))
            if not dia:
                continue
            inicio = _normalizar_hora(match.group(2))
            fin = _normalizar_hora(match.group(3))
            clave = (dia, inicio, fin)
            if clave in vistos:
                continue
            vistos.add(clave)
            resultado.append(
                FranjaHorario(
                    codigo,
                    nombre,
                    nombre_ingles,
                    dia,
                    inicio,
                    fin,
                    "tutoria",
                    "",
                    "",
                    cuatrimestre,
                )
            )
    resultado.sort(key=lambda franja: (franja.dia, franja.inicio, franja.codigo))
    return resultado


def _normalizar_hora(valor: str) -> str:
    horas, minutos = valor.split(":")
    return f"{int(horas):02d}:{minutos}"
