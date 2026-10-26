from dataclasses import dataclass


@dataclass(frozen=True)
class ObtenerMarcasCalendarioQuery:
    anio: int
    mes: int
