from dataclasses import dataclass


@dataclass(frozen=True)
class EliminarUsuarioCommand:
    nick: str
