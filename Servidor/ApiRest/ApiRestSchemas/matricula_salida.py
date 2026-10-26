from pydantic import BaseModel, ConfigDict

from Servidor.ApiRest.ApiRestSchemas.asignatura_salida import AsignaturaSalida
from Servidor.Dominio.DominioEnums.curso_asignatura import CursoAsignatura


class FranjaHorarioSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    codigo: str
    nombre: str
    nombre_ingles: str
    dia: int
    inicio: str
    fin: str
    tipo: str


class TramoCursoSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    curso: CursoAsignatura
    cantidad: int
    porcentaje: int


class MatriculaSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    curso: CursoAsignatura | None
    tramos: list[TramoCursoSalida]
    asignaturas: list[AsignaturaSalida]
    creditos_aprobados: int
    media: float | None
    horario: list[FranjaHorarioSalida]
