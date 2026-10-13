from dataclasses import dataclass


@dataclass(frozen=True)
class AsignarAdministradorCommand:
    email: str
    solicitante_email: str
