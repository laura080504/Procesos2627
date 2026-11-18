from Servidor.Dominio.DominioEntities.asignatura import Asignatura
from Servidor.Dominio.DominioEnums.curso_asignatura import CursoAsignatura


def contar_por_curso(asignaturas: list[Asignatura]) -> dict[CursoAsignatura, int]:
    cantidades: dict[CursoAsignatura, int] = {}
    for asignatura in asignaturas:
        cantidades[asignatura.curso] = cantidades.get(asignatura.curso, 0) + 1
    return cantidades
