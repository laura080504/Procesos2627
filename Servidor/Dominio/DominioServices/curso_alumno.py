from Servidor.Dominio.DominioEntities.asignatura import Asignatura
from Servidor.Dominio.DominioEnums.curso_asignatura import CursoAsignatura
from Servidor.Dominio.DominioServices.conteo_cursos import contar_por_curso


def curso_del_alumno(propias: list[Asignatura]) -> CursoAsignatura | None:
    """Curso del alumno si más de la mitad de sus asignaturas son de ese curso.

    Con empate o sin mayoría estricta no se asigna curso.
    """
    if not propias:
        return None

    total = len(propias)
    umbral_mayoria = total / 2
    cantidades = contar_por_curso(propias)

    curso_elegido = None
    mayor_cantidad = 0
    for curso, cantidad in cantidades.items():
        if cantidad <= umbral_mayoria:
            continue
        if cantidad > mayor_cantidad:
            mayor_cantidad = cantidad
            curso_elegido = curso
    return curso_elegido
