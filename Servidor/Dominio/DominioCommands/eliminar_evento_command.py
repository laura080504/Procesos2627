from dataclasses import dataclass

from Servidor.Dominio.DominioEnums.rol import Rol


@dataclass(frozen=True)
class EliminarEventoCommand:
    evento_id: str
    solicitante_rol: Rol
    solicitante_email: str
