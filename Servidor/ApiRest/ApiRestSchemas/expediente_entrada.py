from pydantic import BaseModel, Field


class CalificacionEntradaSchema(BaseModel):
    codigo: str = Field(min_length=1)
    nota: float | None = None
    convalidada: bool = False


class ExpedienteEntrada(BaseModel):
    calificaciones: list[CalificacionEntradaSchema] = Field(default_factory=list)
