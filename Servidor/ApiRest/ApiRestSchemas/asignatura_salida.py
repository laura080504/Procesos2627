from pydantic import BaseModel, ConfigDict, Field

from Servidor.Dominio.DominioEnums.curso_asignatura import CursoAsignatura


class ProfesorAsignaturaSalida(BaseModel):
    nombre: str
    url: str = ""
    tutorias: list[str] = Field(default_factory=list)


class AsignaturaSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    codigo: str
    nombre: str
    nombre_ingles: str
    curso: CursoAsignatura
    creditos: int
    cuatrimestre: int
    grupo: str = ""
    url_esiiab: str | None = None
    profesores: list[ProfesorAsignaturaSalida] = Field(default_factory=list)
    aulas_teoria: list[str] = Field(default_factory=list)
    aulas_practicas: list[str] = Field(default_factory=list)
