from dataclasses import dataclass

from Servidor.Dominio.DominioEnums.curso_asignatura import CursoAsignatura

EMAIL_LAURA = "lgonzarico@gmail.com"
CONTRASENA_PRUEBA = "prueba1234"

# Álgebra, distribuidos, gestión, programación I, y dos más de otros cursos.
CODIGOS_LAURA = ("42305", "42322", "42304", "42302", "42300", "42314")
# Álgebra queda suspensa para que no sume créditos. El resto aprueba.
NOTAS_LAURA = {
    "42300": 7.0,
    "42302": 8.0,
    "42304": 6.0,
    "42305": 4.0,
    "42314": 9.0,
    "42322": 8.0,
}

ALUMNOS_PRUEBA = (
    {
        "email": "alba@ejemplo.com",
        "nick": "Alba",
        "codigos": ("42300", "42301", "42302", "42303", "42304", "42305", "42306", "42310"),
    },
    {
        "email": "bruno@ejemplo.com",
        "nick": "Bruno",
        "codigos": ("42310", "42311", "42312", "42313", "42314", "42315", "42316", "42320"),
    },
    {
        "email": "celia@ejemplo.com",
        "nick": "Celia",
        "codigos": ("42307", "42308", "42309", "42317", "42318", "42319", "42321"),
    },
)


@dataclass(frozen=True)
class TramoCurso:
    curso: CursoAsignatura
    cantidad: int
    porcentaje: int


def notas_de_muestra(email: str, codigos: tuple[str, ...] | list[str]) -> dict[str, float]:
    if email == EMAIL_LAURA:
        return {codigo: NOTAS_LAURA[codigo] for codigo in codigos if codigo in NOTAS_LAURA}
    return {codigo: float(4 + int(codigo) % 6) for codigo in codigos}


def tramos_de(asignaturas: list) -> list[TramoCurso]:
    if not asignaturas:
        return []
    cantidades: dict[CursoAsignatura, int] = {}
    for asignatura in asignaturas:
        cantidades[asignatura.curso] = cantidades.get(asignatura.curso, 0) + 1
    tramos = []
    acumulado = 0
    cursos = [curso for curso in CursoAsignatura if cantidades.get(curso)]
    for indice, curso in enumerate(cursos):
        if indice == len(cursos) - 1:
            porcentaje = 100 - acumulado
        else:
            porcentaje = round(100 * cantidades[curso] / len(asignaturas))
            acumulado += porcentaje
        tramos.append(TramoCurso(curso, cantidades[curso], porcentaje))
    return tramos
