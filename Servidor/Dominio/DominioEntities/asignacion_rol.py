from dataclasses import dataclass
from datetime import datetime

from Servidor.Dominio.DominioEnums.rol import Rol


@dataclass(frozen=True)
class AsignacionRol:
    """Token hasheado (SHA-256) para confirmar un cambio de rol por correo."""

    token: str
    email: str
    rol_destino: Rol
    expira_en: datetime

    def caducada(self, ahora: datetime) -> bool:
        return ahora >= self.expira_en
