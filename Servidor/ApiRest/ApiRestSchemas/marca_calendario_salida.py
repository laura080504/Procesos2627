from pydantic import BaseModel, ConfigDict


class SimboloCalendarioSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tipo: str
    codigo: str
    nombre: str
    nombre_ingles: str
    hora: str
    fecha: str
    lugar: str | None = None
    evento_id: str | None = None
    editable: bool = False


class MarcaCalendarioSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    dia: int
    simbolos: list[SimboloCalendarioSalida]


class MarcasRangoSalida(BaseModel):
    periodos: dict[str, list[MarcaCalendarioSalida]]
