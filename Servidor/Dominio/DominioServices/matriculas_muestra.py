import random
from dataclasses import dataclass

from Servidor.Dominio.DominioEnums.curso_asignatura import CursoAsignatura
from Servidor.Dominio.DominioServices.catalogo_informatica_albacete import CATALOGO_INFORMATICA_ALBACETE
from Servidor.Dominio.DominioServices.conteo_cursos import contar_por_curso
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas import RepositorioMatriculas

EMAIL_LAURA = "lgonzarico@gmail.com"
CONTRASENA_PRUEBA = "prueba1234"

# Álgebra, distribuidos, gestión, programación I, y dos más de otros cursos.
CODIGOS_LAURA = ("42305", "42322", "42304", "42302", "42300", "42314")
# Cada asignatura puede ir en un grupo distinto (como en la matrícula real).
GRUPOS_LAURA = {
    "42300": "A",
    "42302": "B",
    "42304": "A",
    "42305": "B",
    "42314": "A",
    "42322": "B",
}
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

_CANTIDAD_MUESTRA = 6
_PRINCIPALES_MUESTRA = 4


@dataclass(frozen=True)
class TramoCurso:
    curso: CursoAsignatura
    cantidad: int
    porcentaje: int


def notas_de_muestra(email: str, codigos: tuple[str, ...] | list[str]) -> dict[str, float]:
    if email == EMAIL_LAURA:
        return {codigo: NOTAS_LAURA[codigo] for codigo in codigos if codigo in NOTAS_LAURA}
    return {codigo: float(4 + int(codigo) % 6) for codigo in codigos}


def codigos_aleatorios_para(email: str) -> tuple[str, ...]:
    if email == EMAIL_LAURA:
        return CODIGOS_LAURA
    por_curso: dict[CursoAsignatura, list[str]] = {}
    for asignatura in CATALOGO_INFORMATICA_ALBACETE:
        por_curso.setdefault(asignatura.curso, []).append(asignatura.codigo)
    aleatorio = random.Random(email.strip().lower())
    curso_principal = aleatorio.choice(list(por_curso.keys()))
    principales = por_curso[curso_principal]
    n_principal = min(_PRINCIPALES_MUESTRA, len(principales))
    elegidos = aleatorio.sample(principales, n_principal)
    resto = [codigo for codigo in (a.codigo for a in CATALOGO_INFORMATICA_ALBACETE) if codigo not in elegidos]
    n_extra = min(_CANTIDAD_MUESTRA - n_principal, len(resto))
    if n_extra:
        elegidos.extend(aleatorio.sample(resto, n_extra))
    return tuple(sorted(elegidos))


def grupos_de_muestra(email: str, codigos: tuple[str, ...] | list[str]) -> dict[str, str]:
    if email == EMAIL_LAURA:
        return {codigo: GRUPOS_LAURA.get(codigo, "A") for codigo in codigos}
    letras = ("A", "B", "C")
    return {
        codigo: letras[int(codigo) % len(letras)]
        for codigo in codigos
    }


def asegurar_matricula_de(repositorio_matriculas: RepositorioMatriculas, email: str, codigos: tuple[str, ...] | None = None) -> list[str]:
    email = email.strip().lower()
    actuales = repositorio_matriculas.obtener_codigos(email)
    if actuales:
        repositorio_matriculas.rellenar_notas(email, notas_de_muestra(email, actuales))
        return actuales
    elegidos = list(codigos if codigos is not None else codigos_aleatorios_para(email))
    repositorio_matriculas.reemplazar_alumno(email, elegidos, grupos_de_muestra(email, elegidos))
    repositorio_matriculas.rellenar_notas(email, notas_de_muestra(email, elegidos))
    return elegidos


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
