"""Horario oficial del grupo A de la ESIIAB, curso 2026-27.

Las franjas salen de https://esiiab.uclm.es/horarios/. El aula cuenta como
teoría y el laboratorio (SOFTW, HW, Elect o Lab) como prácticas. En los
cursos con varios grupos se usa el grupo A, el de referencia de la escuela.
"""

L = 0
M = 1
X = 2
J = 3
V = 4


def _t(dia: int, inicio: str, fin: str) -> tuple[int, str, str, str]:
    return (dia, inicio, fin, "teoria")


def _p(dia: int, inicio: str, fin: str) -> tuple[int, str, str, str]:
    return (dia, inicio, fin, "practicas")


SESIONES_ESIIAB: dict[str, tuple[tuple[int, str, str, str], ...]] = {
    "cálculo y métodos numéricos": (
        _t(V, "08:15", "09:45"),
        _t(X, "09:45", "11:15"),
        _t(J, "11:35", "13:05"),
        _t(X, "17:30", "19:00"),
    ),
    "fundamentos físicos de la informática": (
        _t(J, "08:15", "09:45"),
        _t(V, "09:45", "11:15"),
        _p(X, "11:35", "13:05"),
        _p(X, "16:00", "17:30"),
    ),
    "fundamentos de programación i": (
        _t(X, "08:15", "09:45"),
        _t(J, "09:45", "11:15"),
        _p(V, "11:35", "13:05"),
        _p(V, "13:05", "14:35"),
    ),
    "tecnología de computadores": (
        _t(L, "08:15", "09:45"),
        _t(M, "09:45", "11:15"),
        _p(L, "11:35", "13:05"),
        _p(L, "16:00", "17:30"),
    ),
    "fundamentos de gestión empresarial": (
        _t(M, "08:15", "09:45"),
        _t(L, "09:45", "11:15"),
        _t(M, "11:35", "13:05"),
        _p(L, "17:30", "19:00"),
    ),
    "álgebra y matemática discreta": (
        _t(J, "08:15", "09:45"),
        _t(V, "09:45", "11:15"),
        _t(L, "11:35", "13:05"),
        _t(L, "16:00", "17:30"),
    ),
    "fundamentos de programación ii": (
        _t(X, "08:15", "09:45"),
        _t(J, "09:45", "11:15"),
        _p(V, "11:35", "13:05"),
        _p(V, "13:05", "14:35"),
    ),
    "estructura de computadores": (
        _t(V, "08:15", "09:45"),
        _t(L, "09:45", "11:15"),
        _p(M, "11:35", "13:05"),
        _p(L, "17:30", "19:00"),
    ),
    "redes de computadores i": (
        _t(M, "08:15", "09:45"),
        _t(X, "09:45", "11:15"),
        _p(J, "11:35", "13:05"),
        _p(X, "17:30", "19:00"),
    ),
    "sistemas de información": (
        _t(L, "08:15", "09:45"),
        _t(M, "09:45", "11:15"),
        _p(X, "11:35", "13:05"),
        _p(X, "16:00", "17:30"),
    ),
    "lógica": (
        _p(V, "09:45", "11:15"),
        _t(V, "11:35", "13:05"),
        _t(X, "13:05", "14:35"),
        _p(J, "17:30", "19:00"),
    ),
    "organización de computadores": (
        _p(M, "09:45", "11:15"),
        _t(L, "11:35", "13:05"),
        _t(M, "13:05", "14:35"),
        _p(M, "17:30", "19:00"),
    ),
    "estructura de datos": (
        _p(V, "08:15", "09:45"),
        _p(V, "09:45", "11:15"),
        _t(X, "11:35", "13:05"),
        _t(J, "13:05", "14:35"),
    ),
    "sistemas operativos i": (
        _p(L, "09:45", "11:15"),
        _t(M, "11:35", "13:05"),
        _t(L, "13:05", "14:35"),
        _p(M, "16:00", "17:30"),
    ),
    "ingeniería del software i": (
        _p(X, "09:45", "11:15"),
        _t(J, "11:35", "13:05"),
        _t(V, "13:05", "14:35"),
        _p(J, "16:00", "17:30"),
    ),
    "estadística": (
        _p(V, "08:15", "09:45"),
        _p(V, "09:45", "11:15"),
        _t(J, "11:35", "13:05"),
        _t(X, "13:05", "14:35"),
    ),
    "metodología de la programación": (
        _p(L, "09:45", "11:15"),
        _t(V, "11:35", "13:05"),
        _t(J, "13:05", "14:35"),
        _p(M, "16:00", "17:30"),
    ),
    "programación concurrente y tiempo real": (
        _p(J, "09:45", "11:15"),
        _t(X, "11:35", "13:05"),
        _t(M, "13:05", "14:35"),
        _p(J, "17:30", "19:00"),
    ),
    "redes de computadores ii": (
        _p(M, "09:45", "11:15"),
        _t(L, "11:35", "13:05"),
        _t(V, "13:05", "14:35"),
        _p(M, "17:30", "19:00"),
    ),
    "bases de datos": (
        _p(X, "09:45", "11:15"),
        _t(M, "11:35", "13:05"),
        _t(L, "13:05", "14:35"),
        _p(J, "16:00", "17:30"),
    ),
    "ingeniería del software ii": (
        _t(L, "08:15", "09:45"),
        _t(M, "09:45", "11:15"),
        _p(J, "11:35", "13:05"),
        _p(X, "17:30", "19:00"),
    ),
    "sistemas distribuidos": (
        _t(M, "08:15", "09:45"),
        _t(X, "09:45", "11:15"),
        _p(V, "11:35", "13:05"),
        _p(V, "13:05", "14:35"),
    ),
    "interacción persona-ordenador i": (
        _t(X, "08:15", "09:45"),
        _t(J, "09:45", "11:15"),
        _p(L, "11:35", "13:05"),
        _p(L, "16:00", "17:30"),
    ),
    "sistemas inteligentes": (
        _t(J, "08:15", "09:45"),
        _t(V, "09:45", "11:15"),
        _p(X, "11:35", "13:05"),
        _p(X, "16:00", "17:30"),
    ),
    "arquitectura de computadores": (
        _t(V, "08:15", "09:45"),
        _t(L, "09:45", "11:15"),
        _p(M, "11:35", "13:05"),
        _p(L, "17:30", "19:00"),
    ),
    "aspectos profesionales de la informática": (
        _t(L, "11:35", "13:05"),
        _t(M, "11:35", "13:05"),
        _p(X, "11:35", "13:05"),
        _p(J, "11:35", "13:05"),
        _t(L, "13:05", "14:35"),
        _t(M, "13:05", "14:35"),
        _p(X, "13:05", "14:35"),
        _p(J, "13:05", "14:35"),
    ),
    "ingeniería de requisitos": (
        _t(L, "08:15", "09:45"),
        _t(M, "09:45", "11:15"),
        _t(L, "17:30", "19:00"),
    ),
    "diseño de software": (
        _t(J, "08:15", "09:45"),
        _t(X, "09:45", "11:15"),
        _t(J, "09:45", "11:15"),
    ),
    "desarrollo de bases de datos": (
        _t(M, "08:15", "09:45"),
        _t(L, "09:45", "11:15"),
        _t(L, "16:00", "17:30"),
    ),
    "sistemas de información empresariales": (
        _t(X, "08:15", "09:45"),
        _t(V, "08:15", "09:45"),
        _t(V, "09:45", "11:15"),
    ),
    "sistemas operativos ii": (
        _t(J, "08:15", "09:45"),
        _p(V, "08:15", "09:45"),
        _t(X, "09:45", "11:15"),
    ),
    "diseño de sistemas basados en microprocesador": (
        _t(X, "08:15", "09:45"),
        _t(J, "09:45", "11:15"),
        _p(V, "09:45", "11:15"),
    ),
    "gestión y administración de redes": (
        _t(L, "08:15", "09:45"),
        _p(M, "09:45", "11:15"),
        _p(L, "17:30", "19:00"),
    ),
    "diseño de infraestructura de red": (
        _p(M, "08:15", "09:45"),
        _t(L, "09:45", "11:15"),
        _p(L, "16:00", "17:30"),
    ),
    "teoría de autómatas y computación": (
        _t(X, "08:15", "09:45"),
        _t(J, "09:45", "11:15"),
        _t(V, "09:45", "11:15"),
    ),
    "programación declarativa": (
        _t(L, "08:15", "09:45"),
        _t(M, "09:45", "11:15"),
        _t(L, "17:30", "19:00"),
    ),
    "diseño de algoritmos": (
        _t(J, "08:15", "09:45"),
        _t(V, "08:15", "09:45"),
        _t(X, "09:45", "11:15"),
    ),
    "sistemas basados en el conocimiento": (
        _t(M, "08:15", "09:45"),
        _t(L, "09:45", "11:15"),
        _t(L, "16:00", "17:30"),
    ),
    "integración de sistemas informáticos": (
        _t(L, "08:15", "09:45"),
        _t(M, "09:45", "11:15"),
        _p(L, "17:30", "19:00"),
    ),
    "interacción persona-ordenador ii": (
        _t(X, "08:15", "09:45"),
        _t(J, "09:45", "11:15"),
        _t(V, "09:45", "11:15"),
    ),
    "diseño y gestión de redes": (
        _t(J, "08:15", "09:45"),
        _t(X, "09:45", "11:15"),
        _p(V, "08:15", "09:45"),
    ),
    "gestión de sistemas de información": (
        _t(M, "08:15", "09:45"),
        _t(L, "09:45", "11:15"),
        _p(L, "16:00", "17:30"),
    ),
    "procesos de ingeniería del software": (
        _t(X, "11:35", "13:05"),
        _t(J, "13:05", "14:35"),
        _t(M, "17:30", "19:00"),
    ),
    "calidad de sistemas software": (
        _t(M, "11:35", "13:05"),
        _t(L, "13:05", "14:35"),
        _t(V, "11:35", "13:05"),
    ),
    "gestión de proyectos software": (
        _t(L, "11:35", "13:05"),
        _t(M, "13:05", "14:35"),
        _p(M, "16:00", "17:35"),
    ),
    "seguridad de sistemas software": (
        _t(J, "11:35", "13:05"),
        _t(X, "13:05", "14:35"),
        _t(V, "13:05", "14:35"),
    ),
    "computadores avanzados": (
        _t(J, "11:35", "13:05"),
        _t(X, "13:05", "14:35"),
        _p(V, "13:05", "14:35"),
    ),
    "sistemas empotrados": (
        _p(L, "13:05", "14:35"),
        _p(M, "16:00", "19:00"),
    ),
    "seguridad en redes": (
        _t(X, "11:35", "13:05"),
        _t(J, "13:05", "14:35"),
        _t(V, "11:35", "13:05"),
    ),
    "planificación e integración de sistemas y servicios": (
        _t(L, "11:35", "13:05"),
        _p(M, "11:35", "13:05"),
        _p(M, "13:05", "14:35"),
    ),
    "sistemas multiagentes": (
        _t(X, "11:35", "13:05"),
        _t(J, "13:05", "14:35"),
        _t(V, "13:05", "14:35"),
    ),
    "diseño de sistemas interactivos": (
        _t(M, "11:35", "13:05"),
        _t(L, "13:05", "14:35"),
        _t(M, "17:30", "19:00"),
    ),
    "minería de datos": (
        _t(L, "11:35", "13:05"),
        _t(M, "13:05", "14:35"),
        _p(M, "16:00", "17:30"),
    ),
    "procesadores de lenguajes": (
        _t(J, "11:35", "13:05"),
        _t(X, "13:05", "14:35"),
        _p(V, "11:35", "13:05"),
    ),
    "tecnologías y sistemas web": (
        _t(M, "11:35", "13:05"),
        _t(L, "13:05", "14:35"),
        _p(M, "17:30", "19:00"),
    ),
    "comercio electrónico": (
        _t(L, "11:35", "13:05"),
        _t(M, "13:05", "14:35"),
        _p(M, "16:00", "17:30"),
    ),
    "multimedia": (
        _t(X, "11:35", "13:05"),
        _t(J, "13:05", "14:35"),
        _p(V, "11:35", "13:05"),
    ),
    "seguridad en sistemas informáticos": (
        _t(J, "11:35", "13:05"),
        _t(X, "13:05", "14:35"),
        _t(V, "13:05", "14:35"),
    ),
    "ingeniería web y de servicios": (
        _p(L, "08:15", "09:45"),
        _p(L, "09:45", "11:15"),
        _p(M, "09:45", "11:15"),
    ),
    "auditoría de sistemas de información": (
        _t(M, "08:15", "09:45"),
        _t(X, "09:45", "11:15"),
        _t(J, "09:45", "11:15"),
    ),
}


def _clave(nombre: str) -> str:
    traduccion = str.maketrans("áéíóúü", "aeiouu")
    return " ".join(nombre.lower().translate(traduccion).split())


_POR_CLAVE = {_clave(nombre): sesiones for nombre, sesiones in SESIONES_ESIIAB.items()}


def sesiones_de(nombre: str) -> tuple[tuple[int, str, str, str], ...]:
    return _POR_CLAVE.get(_clave(nombre), ())
