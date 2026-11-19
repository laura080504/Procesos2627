"""Menciones (tecnología específica) del plan 406 · Albacete.

Las 8 asignaturas de cada mención son excluyentes entre sí: si el alumno
está en Ingeniería del Software, las de Computadores/Computación/TI no
cuentan como pendientes.
"""

from __future__ import annotations

from Servidor.Dominio.DominioEnums.intensificacion import Intensificacion

CODIGOS_POR_INTENSIFICACION: dict[Intensificacion, frozenset[str]] = {
    Intensificacion.SOFTWARE: frozenset(
        {
            "42326",
            "42327",
            "42328",
            "42329",
            "42330",
            "42331",
            "42332",
            "42333",
        }
    ),
    Intensificacion.COMPUTADORES: frozenset(
        {
            "42334",
            "42335",
            "42336",
            "42337",
            "42338",
            "42339",
            "42340",
            "42341",
        }
    ),
    Intensificacion.COMPUTACION: frozenset(
        {
            "42342",
            "42343",
            "42344",
            "42345",
            "42346",
            "42347",
            "42348",
            "42349",
        }
    ),
    Intensificacion.TECNOLOGIAS_INFORMACION: frozenset(
        {
            "42350",
            "42351",
            "42352",
            "42353",
            "42354",
            "42355",
            "42356",
            "42357",
        }
    ),
}

# Optativas libres / extracurriculares: no se listan como "te quedan" en bloque.
CODIGOS_OPTATIVAS_LIBRES = frozenset(
    {
        "42366",
        "42373",
        "42381",
        "42382",
        "42386",
        "42387",
        "42392",
        "42393",
        "42395",
        "42396",
        "42397",
        "42398",
        "42399",
    }
)

_TODAS_MENCION = frozenset().union(*CODIGOS_POR_INTENSIFICACION.values())


def pertenece_a_otra_intensificacion(codigo: str, intensificacion: Intensificacion | None) -> bool:
    if codigo not in _TODAS_MENCION:
        return False
    if intensificacion is None:
        return True
    propias = CODIGOS_POR_INTENSIFICACION[intensificacion]
    return codigo not in propias


def es_pendiente_del_plan(
    codigo: str,
    intensificacion: Intensificacion | None,
    *,
    activas: set[str] | frozenset[str] | None = None,
) -> bool:
    """Asignaturas que aún "quedan" según la mención del alumno.

    - Comunes: sí
    - De su mención: sí
    - De otras menciones: no
    - Optativas libres: solo si están en matrícula activa (las elige la escuela)
    - TFG: sí
    """
    if codigo == "42358":
        return True
    if codigo in CODIGOS_OPTATIVAS_LIBRES:
        return bool(activas and codigo in activas)
    if pertenece_a_otra_intensificacion(codigo, intensificacion):
        return False
    if codigo in _TODAS_MENCION and intensificacion is None:
        return False
    return True
