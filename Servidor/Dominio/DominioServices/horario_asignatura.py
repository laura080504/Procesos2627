from dataclasses import dataclass

from Servidor.Dominio.DominioEntities.asignatura import Asignatura
from Servidor.Dominio.DominioServices.horario_esiiab import sesiones_de


@dataclass(frozen=True)
class FranjaHorario:
    codigo: str
    nombre: str
    nombre_ingles: str
    dia: int
    inicio: str
    fin: str
    tipo: str
    aula: str = ""
    grupo: str = ""


def franjas_de(
    asignaturas: list[Asignatura],
    grupos_por_codigo: dict[str, str] | None = None,
) -> list[FranjaHorario]:
    """Cruza asignaturas matriculadas con el horario ESIIAB.

    Si se indica grupo por código, solo se incluyen las franjas de ese grupo.
    """
    franjas = []
    grupos = grupos_por_codigo or {}
    for asignatura in asignaturas:
        grupo_alumno = (grupos.get(asignatura.codigo) or "").strip()
        for dia, inicio, fin, tipo, aula, grupo in _desempaquetar(sesiones_de(asignatura.nombre)):
            if grupo_alumno and grupo and grupo_alumno != grupo:
                continue
            franjas.append(
                FranjaHorario(
                    asignatura.codigo,
                    asignatura.nombre,
                    asignatura.nombre_ingles,
                    dia,
                    inicio,
                    fin,
                    tipo,
                    aula,
                    grupo or grupo_alumno,
                )
            )
    franjas.sort(key=lambda franja: (franja.dia, franja.inicio, franja.codigo, franja.grupo))
    return franjas


def aulas_de(franjas: list[FranjaHorario], codigo: str, grupo: str | None = None) -> tuple[list[str], list[str]]:
    teoria: list[str] = []
    practicas: list[str] = []
    for franja in franjas:
        if franja.codigo != codigo or not franja.aula:
            continue
        if grupo and franja.grupo and franja.grupo != grupo:
            continue
        destino = practicas if franja.tipo == "practicas" else teoria
        if franja.aula not in destino:
            destino.append(franja.aula)
    return teoria, practicas


def _desempaquetar(sesiones) -> list[tuple[int, str, str, str, str, str]]:
    resultado = []
    for sesion in sesiones:
        if len(sesion) >= 6:
            resultado.append((sesion[0], sesion[1], sesion[2], sesion[3], sesion[4], sesion[5]))
        elif len(sesion) == 5:
            resultado.append((sesion[0], sesion[1], sesion[2], sesion[3], sesion[4], ""))
        else:
            dia, inicio, fin, tipo = sesion[:4]
            resultado.append((dia, inicio, fin, tipo, "", ""))
    return resultado
