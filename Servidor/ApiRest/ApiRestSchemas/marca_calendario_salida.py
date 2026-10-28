from pydantic import BaseModel, ConfigDict


class SimboloCalendarioSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tipo: str
    codigo: str
    nombre: str
    nombre_ingles: str
    hora: str
    lugar: str | None = None


class MarcaCalendarioSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    dia: int
    simbolos: list[SimboloCalendarioSalida]
