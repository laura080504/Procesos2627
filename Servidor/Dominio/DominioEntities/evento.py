from dataclasses import dataclass
from datetime import date

from Servidor.Dominio.DominioEnums.tipo_evento import TipoEvento


@dataclass(frozen=True)
class Evento:
    fecha: date
    codigo: str
    tipo: TipoEvento
    hora: str
    lugar: str | None = None
