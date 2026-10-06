from dataclasses import dataclass


@dataclass(frozen=True)
class IniciarSesionCommand:
    email: str
    contrasena: str
