from dataclasses import dataclass
from datetime import date

from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Dominio.DominioEnums.tipo_evento import TipoEvento


@dataclass(frozen=True)
class CrearEventoCommand:
    codigo: str
    tipo: TipoEvento
    fecha: date
    hora: str
    lugar: str | None
    solicitante_rol: Rol
    solicitante_email: str = ""
