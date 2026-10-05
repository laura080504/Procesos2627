from dataclasses import dataclass


@dataclass(frozen=True)
class RegistrarUsuarioCommand:
    email: str
    nick: str
    contrasena: str
