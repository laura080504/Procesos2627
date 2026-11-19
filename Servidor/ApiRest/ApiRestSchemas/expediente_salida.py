from pydantic import BaseModel, ConfigDict, Field

from Servidor.ApiRest.ApiRestSchemas.matricula_salida import TramoCursoSalida
from Servidor.Dominio.DominioEnums.curso_asignatura import CursoAsignatura


class AsignaturaExpedienteSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    codigo: str
    nombre: str
    nombre_ingles: str
    curso: CursoAsignatura
    creditos: int
    cuatrimestre: int
    nota: float | None = None
    convalidada: bool = False


class ExpedienteSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    curso: CursoAsignatura | None
    tramos: list[TramoCursoSalida]
    calificadas: list[AsignaturaExpedienteSalida]
    pendientes: list[AsignaturaExpedienteSalida]
    creditos_aprobados: int
    creditos_convalidados: int
    media: float | None
    intensificacion: str | None = None
    origen: str = Field(default="manual", description="manual hasta tener API de secretaría")
