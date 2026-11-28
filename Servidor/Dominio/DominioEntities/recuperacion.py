from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Recuperacion:
    """El campo token guarda el HASH SHA-256 del token enviado al usuario."""

    token: str
    email: str
    expira_en: datetime

    def caducada(self, ahora: datetime) -> bool:
        return ahora >= self.expira_en
