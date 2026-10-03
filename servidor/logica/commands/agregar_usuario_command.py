from dataclasses import dataclass


@dataclass(frozen=True)
class AgregarUsuarioCommand:
    nick: str
