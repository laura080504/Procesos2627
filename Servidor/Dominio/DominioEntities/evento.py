from dataclasses import dataclass
from datetime import date
from uuid import uuid4

from Servidor.Dominio.DominioEnums.tipo_evento import TipoEvento


@dataclass(frozen=True)
class Evento:
    fecha: date
    codigo: str
    tipo: TipoEvento
    hora: str
    lugar: str | None = None
    id: str | None = None

    def con_id(self) -> "Evento":
        if self.id:
            return self
        return Evento(
            fecha=self.fecha,
            codigo=self.codigo,
            tipo=self.tipo,
            hora=self.hora,
            lugar=self.lugar,
            id=nuevo_id_evento(),
        )


def nuevo_id_evento() -> str:
    return uuid4().hex


def identidad_evento(evento: Evento) -> str:
    if evento.id:
        return evento.id
    return f"{evento.fecha.isoformat()}|{evento.codigo}|{evento.tipo.value}|{evento.hora}"
