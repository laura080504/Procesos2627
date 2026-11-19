from dataclasses import dataclass

from Servidor.Dominio.DominioEnums.curso_asignatura import CursoAsignatura
from Servidor.Dominio.DominioServices.conteo_cursos import contar_por_curso
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas import RepositorioMatriculas

EMAIL_LAURA = "lgonzarico@gmail.com"
CONTRASENA_PRUEBA = "prueba1234"
INTENSIFICACION_LAURA = "software"

# Matrícula real de Laura (campus UCLM).
CODIGOS_LAURA = (
    "42305",
    "42322",
    "42324",
    "42325",
    "42326",
    "42327",
    "42328",
    "42330",
    "42332",
    "42333",
    "42366",
)
GRUPOS_LAURA = {
    "42305": "13",
    "42322": "11",
    "42324": "11",
    "42325": "11",
    "42326": "14",
    "42327": "14",
    "42328": "14",
    "42330": "14",
    "42332": "14",
    "42333": "14",
    "42366": "17",
}

ALUMNOS_PRUEBA = (
    {"email": "alba@ejemplo.com", "nick": "Alba"},
    {"email": "bruno@ejemplo.com", "nick": "Bruno"},
    {"email": "celia@ejemplo.com", "nick": "Celia"},
)


@dataclass(frozen=True)
class TramoCurso:
    curso: CursoAsignatura
    cantidad: int
    porcentaje: int


def asegurar_matricula_de(
    repositorio_matriculas: RepositorioMatriculas,
    email: str,
    codigos: tuple[str, ...] | None = None,
) -> list[str]:
    """Solo siembra la matrícula oficial de Laura. El resto queda vacío hasta que la editen."""
    email = email.strip().lower()
    actuales = repositorio_matriculas.obtener_codigos(email)
    if not actuales:
        if email == EMAIL_LAURA:
            elegidos = list(codigos if codigos is not None else CODIGOS_LAURA)
            repositorio_matriculas.reemplazar_alumno(email, elegidos, dict(GRUPOS_LAURA))
            actuales = elegidos
        elif codigos:
            elegidos = list(codigos)
            repositorio_matriculas.reemplazar_alumno(email, elegidos, {codigo: "A" for codigo in elegidos})
            actuales = elegidos
    if email == EMAIL_LAURA:
        asegurar_expediente_laura(repositorio_matriculas)
    return actuales


def asegurar_expediente_laura(repositorio_matriculas: RepositorioMatriculas) -> None:
    """Solo marca intensificación Software. Las notas NUNCA van en código: solo BBDD vía Historial."""
    email = EMAIL_LAURA
    if not repositorio_matriculas.obtener_intensificacion(email):
        repositorio_matriculas.guardar_intensificacion(email, INTENSIFICACION_LAURA)


def forzar_matricula_laura(repositorio_matriculas: RepositorioMatriculas) -> None:
    repositorio_matriculas.reemplazar_alumno(EMAIL_LAURA, list(CODIGOS_LAURA), dict(GRUPOS_LAURA))
    repositorio_matriculas.guardar_intensificacion(EMAIL_LAURA, INTENSIFICACION_LAURA)


def tramos_de(asignaturas: list) -> list[TramoCurso]:
    """Porcentaje de asignaturas por curso; el último tramo absorbe el redondeo para sumar 100."""
    if not asignaturas:
        return []

    cantidades = contar_por_curso(asignaturas)
    cursos = [curso for curso in CursoAsignatura if cantidades.get(curso)]
    total = len(asignaturas)
    tramos = []
    porcentaje_acumulado = 0

    for indice, curso in enumerate(cursos):
        es_ultimo = indice == len(cursos) - 1
        if es_ultimo:
            porcentaje = 100 - porcentaje_acumulado
        else:
            porcentaje = round(100 * cantidades[curso] / total)
            porcentaje_acumulado += porcentaje
        tramos.append(TramoCurso(curso, cantidades[curso], porcentaje))
    return tramos
