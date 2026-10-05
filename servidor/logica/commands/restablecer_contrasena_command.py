from dataclasses import dataclass


@dataclass(frozen=True)
class RestablecerContrasenaCommand:
    token: str
    contrasena: str
