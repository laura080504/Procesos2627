from dataclasses import dataclass


@dataclass(frozen=True)
class SimboloCalendario:
    tipo: str
    codigo: str
    nombre: str
    nombre_ingles: str


@dataclass(frozen=True)
class MarcaCalendario:
    dia: int
    simbolos: list[SimboloCalendario]
