from dataclasses import dataclass

from Servidor.Dominio.DominioEnums.rol import Rol


@dataclass(frozen=True)
class ObtenerUsuariosQuery:
    solicitante_rol: Rol | None = None
    solicitante_email: str = ""
