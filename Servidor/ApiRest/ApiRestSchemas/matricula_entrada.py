from pydantic import BaseModel, Field


class AsignaturaMatriculaEntradaSchema(BaseModel):
    codigo: str = Field(min_length=1, max_length=16)
    grupo: str = Field(default="A", min_length=1, max_length=24)


class MatriculaEntrada(BaseModel):
    asignaturas: list[AsignaturaMatriculaEntradaSchema] = Field(min_length=1)
