from dataclasses import dataclass


@dataclass(frozen=True)
class ListarAsignaturasQuery:
    nombre: str = ""
