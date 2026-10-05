from dataclasses import dataclass


@dataclass(frozen=True)
class ObtenerUsuarioSesionQuery:
    token: str
