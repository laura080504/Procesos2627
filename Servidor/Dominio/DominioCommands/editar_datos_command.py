from dataclasses import dataclass


@dataclass(frozen=True)
class EditarDatosCommand:
    solicitante_email: str
    email: str
    nick: str
    contrasena: str | None = None
