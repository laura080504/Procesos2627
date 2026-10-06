from dataclasses import dataclass


@dataclass(frozen=True)
class EliminarUsuarioCommand:
    email: str
