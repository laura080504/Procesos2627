from datetime import date

from pydantic import BaseModel, Field

from Servidor.Dominio.DominioEnums.tipo_evento import TipoEvento


class EventoEntrada(BaseModel):
    codigo: str = Field(min_length=1, max_length=16)
    tipo: TipoEvento
    fecha: date
    hora: str = Field(min_length=4, max_length=5)
    lugar: str | None = Field(default=None, max_length=80)
