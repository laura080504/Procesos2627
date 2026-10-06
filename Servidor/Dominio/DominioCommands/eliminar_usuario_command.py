from dataclasses import dataclass

from Servidor.Dominio.DominioEnums.rol import Rol


@dataclass(frozen=True)
class EliminarUsuarioCommand:
    email: str
    solicitante_email: str
    solicitante_rol: Rol
