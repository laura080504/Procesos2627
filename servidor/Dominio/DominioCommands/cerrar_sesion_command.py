from dataclasses import dataclass


@dataclass(frozen=True)
class CerrarSesionCommand:
    token: str
