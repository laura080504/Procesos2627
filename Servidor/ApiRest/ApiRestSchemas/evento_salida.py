from datetime import date

from pydantic import BaseModel, ConfigDict

from Servidor.Dominio.DominioEnums.tipo_evento import TipoEvento


class EventoSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str | None = None
    fecha: date
    codigo: str
    tipo: TipoEvento
    hora: str
    lugar: str | None = None
    nombre: str | None = None
    nombre_ingles: str | None = None
