from Servidor.Dominio.DominioEntities.asignatura import Asignatura
from Servidor.Dominio.DominioEnums.curso_asignatura import CursoAsignatura


def curso_del_alumno(propias: list[Asignatura]) -> CursoAsignatura | None:
    if not propias:
        return None
    cantidades: dict[CursoAsignatura, int] = {}
    for asignatura in propias:
        cantidades[asignatura.curso] = cantidades.get(asignatura.curso, 0) + 1
    total = len(propias)
    elegido = None
    mejor = 0
    for curso, cantidad in cantidades.items():
        if cantidad * 2 <= total:
            continue
        if cantidad > mejor:
            mejor = cantidad
            elegido = curso
    return elegido
