from dataclasses import dataclass

from Servidor.Dominio.DominioEntities.asignatura import Asignatura
from Servidor.Dominio.DominioEntities.evento import Evento
from Servidor.Dominio.DominioEnums.tipo_evento import TipoEvento

_TIPO_SIMBOLO = {
    TipoEvento.EXAMEN: "estrella",
    TipoEvento.ENTREGA: "punto",
}


@dataclass(frozen=True)
class SimboloCalendario:
    tipo: str
    codigo: str
    nombre: str
    nombre_ingles: str
    hora: str
    fecha: str
    lugar: str | None = None


@dataclass(frozen=True)
class MarcaCalendario:
    dia: int
    simbolos: list[SimboloCalendario]


def marcas_del_mes(
    eventos: list[Evento],
    asignaturas_por_codigo: dict[str, Asignatura],
    anio: int,
    mes: int,
) -> list[MarcaCalendario]:
    por_dia: dict[int, list[Evento]] = {}
    for evento in eventos:
        if evento.fecha.year != anio or evento.fecha.month != mes:
            continue
        por_dia.setdefault(evento.fecha.day, []).append(evento)

    marcas = []
    for dia in sorted(por_dia):
        del_dia = sorted(por_dia[dia], key=_prioridad_en_dia)
        simbolos = [_simbolo_de(evento, asignaturas_por_codigo.get(evento.codigo)) for evento in del_dia]
        marcas.append(MarcaCalendario(dia, simbolos))
    return marcas


def _prioridad_en_dia(evento: Evento) -> int:
    # Los exámenes van delante de las entregas en el mismo día.
    if evento.tipo == TipoEvento.EXAMEN:
        return 0
    return 1


def _simbolo_de(evento: Evento, asignatura: Asignatura | None) -> SimboloCalendario:
    return SimboloCalendario(
        tipo=_TIPO_SIMBOLO[evento.tipo],
        codigo=evento.codigo,
        nombre=asignatura.nombre if asignatura else evento.codigo,
        nombre_ingles=asignatura.nombre_ingles if asignatura else evento.codigo,
        hora=evento.hora,
        fecha=evento.fecha.isoformat(),
        lugar=evento.lugar,
    )
