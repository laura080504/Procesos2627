from pydantic import BaseModel, ConfigDict


class SimboloCalendarioSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tipo: str
    codigo: str
    nombre: str
    nombre_ingles: str


class MarcaCalendarioSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    dia: int
    simbolos: list[SimboloCalendarioSalida]
