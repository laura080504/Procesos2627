from dataclasses import dataclass


@dataclass(frozen=True)
class UsuarioActivoQuery:
    nick: str
