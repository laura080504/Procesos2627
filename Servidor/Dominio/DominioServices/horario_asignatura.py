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


def franjas_de(asignaturas: list[Asignatura]) -> list[FranjaHorario]:
    franjas = []
    for asignatura in asignaturas:
        for dia, inicio, fin, tipo in sesiones_de(asignatura.nombre):
            franjas.append(
                FranjaHorario(
                    asignatura.codigo,
                    asignatura.nombre,
                    asignatura.nombre_ingles,
                    dia,
                    inicio,
                    fin,
                    tipo,
                )
            )
    franjas.sort(key=lambda franja: (franja.dia, franja.inicio, franja.codigo))
    return franjas
