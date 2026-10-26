from dataclasses import dataclass

from Servidor.Dominio.DominioEnums.curso_asignatura import CursoAsignatura


@dataclass(frozen=True)
class Asignatura:
    codigo: str
    nombre: str
    nombre_ingles: str
    curso: CursoAsignatura
    creditos: int
    cuatrimestre: int
