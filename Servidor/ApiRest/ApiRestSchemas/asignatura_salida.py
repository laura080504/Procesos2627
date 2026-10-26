from pydantic import BaseModel, ConfigDict

from Servidor.Dominio.DominioEnums.curso_asignatura import CursoAsignatura


class AsignaturaSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    codigo: str
    nombre: str
    nombre_ingles: str
    curso: CursoAsignatura
    creditos: int
    cuatrimestre: int
