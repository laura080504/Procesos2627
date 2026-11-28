from dataclasses import dataclass
from datetime import date, timedelta

from Servidor.Dominio.DominioEntities.asignatura import Asignatura
from Servidor.Dominio.DominioEntities.evento import Evento, identidad_evento
from Servidor.Dominio.DominioEnums.tipo_evento import TipoEvento
from Servidor.Dominio.DominioServices.normalizar_texto import normalizar_texto
from Servidor.Dominio.DominioServices.parser_calendario_esiiab import CalendarioAcademicoEsiiab, FechaAcademica
from Servidor.Dominio.DominioServices.parser_examenes_esiiab import ExamenEsiiab, ExamenesEsiiab

_TIPO_SIMBOLO = {
    TipoEvento.EXAMEN: "estrella",
    TipoEvento.ENTREGA: "punto",
}

_TIPOS_CAMBIO_CUATRI = {"inicio_cuatrimestre", "fin_cuatrimestre"}
_TIPOS_MARCA_DIRECTA = {"festivo", "vacaciones"} | _TIPOS_CAMBIO_CUATRI


@dataclass(frozen=True)
class SimboloCalendario:
    tipo: str
    codigo: str
    nombre: str
    nombre_ingles: str
    hora: str
    fecha: str
    lugar: str | None = None
    evento_id: str | None = None
    editable: bool = False


@dataclass(frozen=True)
class MarcaCalendario:
    dia: int
    simbolos: list[SimboloCalendario]


def marcas_del_mes(
    eventos: list[Evento],
    asignaturas_por_codigo: dict[str, Asignatura],
    anio: int,
    mes: int,
    examenes: ExamenesEsiiab | None = None,
    calendario: CalendarioAcademicoEsiiab | None = None,
) -> list[MarcaCalendario]:
    oficiales = _examenes_como_eventos(examenes, asignaturas_por_codigo) if examenes else []
    oficiales_clave = {(evento.codigo, evento.fecha) for evento in oficiales}
    propios = [
        evento
        for evento in eventos
        if not (evento.tipo == TipoEvento.EXAMEN and (evento.codigo, evento.fecha) in oficiales_clave)
    ]

    por_dia: dict[int, list[SimboloCalendario]] = {}
    for evento in propios:
        if evento.fecha.year != anio or evento.fecha.month != mes:
            continue
        por_dia.setdefault(evento.fecha.day, []).append(
            _simbolo_de(evento, asignaturas_por_codigo.get(evento.codigo), editable=True)
        )
    for evento in oficiales:
        if evento.fecha.year != anio or evento.fecha.month != mes:
            continue
        por_dia.setdefault(evento.fecha.day, []).append(
            _simbolo_de(evento, asignaturas_por_codigo.get(evento.codigo), editable=False)
        )

    for dia, fechas in _fechas_academicas_del_mes(calendario, anio, mes).items():
        for fecha in fechas:
            por_dia.setdefault(dia, []).append(_simbolo_academico(fecha, date(anio, mes, dia)))

    marcas = []
    for dia in sorted(por_dia):
        simbolos = sorted(por_dia[dia], key=_prioridad_simbolo)
        marcas.append(MarcaCalendario(dia, simbolos))
    return marcas


def _examenes_como_eventos(
    examenes: ExamenesEsiiab,
    asignaturas_por_codigo: dict[str, Asignatura],
) -> list[Evento]:
    por_nombre = {
        normalizar_texto(asignatura.nombre): asignatura for asignatura in asignaturas_por_codigo.values()
    }
    eventos: list[Evento] = []
    for examen in examenes.examenes:
        asignatura = por_nombre.get(normalizar_texto(examen.nombre))
        if asignatura is None:
            continue
        lugar = _lugar_examen(examen)
        eventos.append(
            Evento(
                fecha=examen.fecha,
                codigo=asignatura.codigo,
                tipo=TipoEvento.EXAMEN,
                hora=examen.hora or "00:00",
                lugar=lugar,
            )
        )
    return eventos


def _lugar_examen(examen: ExamenEsiiab) -> str | None:
    partes = [parte for parte in (examen.centro, examen.aulas) if parte]
    if not partes:
        return None
    texto = " · ".join(partes)
    if examen.convocatoria == "extraordinaria":
        return f"{texto} (extra)"
    return texto


def _fechas_academicas_del_mes(
    calendario: CalendarioAcademicoEsiiab | None,
    anio: int,
    mes: int,
) -> dict[int, list[FechaAcademica]]:
    if calendario is None:
        return {}
    por_dia: dict[int, list[FechaAcademica]] = {}
    for fecha in calendario.fechas:
        if fecha.tipo in _TIPOS_MARCA_DIRECTA:
            _volcar_rango(por_dia, fecha, anio, mes)
    for periodo in _periodos_examen(calendario.fechas):
        _volcar_rango(por_dia, periodo, anio, mes)
    return por_dia


def _periodos_examen(fechas: tuple[FechaAcademica, ...]) -> list[FechaAcademica]:
    """Empareja cada inicio con un fin distinto (el más cercano posterior).

    En la ESIIAB a veces hay dos calendarios a la vez (p. ej. fin el 25/06 y
    el 02/07); si reutilizásemos el mismo fin, julio quedaría sin marcar.
    """
    pares = (
        ("inicio_examenes_ordinarios", "fin_examenes_ordinarios", "semana_examenes_ordinarios"),
        ("inicio_examenes_extraordinarios", "fin_examenes_extraordinarios", "semana_examenes_extraordinarios"),
    )
    resultado: list[FechaAcademica] = []
    for inicio_tipo, fin_tipo, tipo_periodo in pares:
        inicios = sorted((f for f in fechas if f.tipo == inicio_tipo), key=lambda item: item.inicio)
        fines = sorted((f for f in fechas if f.tipo == fin_tipo), key=lambda item: item.inicio)
        usados: set[int] = set()
        for inicio in inicios:
            elegido = None
            for indice, fin in enumerate(fines):
                if indice in usados or fin.inicio < inicio.inicio:
                    continue
                elegido = (indice, fin)
                break
            if elegido is None:
                continue
            indice, fin = elegido
            usados.add(indice)
            resultado.append(FechaAcademica(tipo_periodo, inicio.titulo, inicio.inicio, fin.fin))
    return resultado


def _volcar_rango(
    por_dia: dict[int, list[FechaAcademica]],
    fecha: FechaAcademica,
    anio: int,
    mes: int,
) -> None:
    actual = fecha.inicio
    while actual <= fecha.fin:
        if actual.year == anio and actual.month == mes:
            existentes = por_dia.setdefault(actual.day, [])
            if not any(item.titulo == fecha.titulo and item.tipo == fecha.tipo for item in existentes):
                existentes.append(fecha)
        actual += timedelta(days=1)
        if actual - fecha.inicio > timedelta(days=120):
            break


def _prioridad_simbolo(simbolo: SimboloCalendario) -> tuple[int, str, str]:
    orden = {
        "estrella": 0,
        "punto": 1,
        "cambio_cuatrimestre": 2,
        "festivo": 3,
        "vacaciones": 4,
        "semana_examenes": 5,
        "periodo": 6,
    }
    return (orden.get(simbolo.tipo, 9), simbolo.hora or "", simbolo.nombre)


def _simbolo_de(
    evento: Evento,
    asignatura: Asignatura | None,
    editable: bool,
) -> SimboloCalendario:
    return SimboloCalendario(
        tipo=_TIPO_SIMBOLO[evento.tipo],
        codigo=evento.codigo,
        nombre=asignatura.nombre if asignatura else evento.codigo,
        nombre_ingles=asignatura.nombre_ingles if asignatura else evento.codigo,
        hora=evento.hora,
        fecha=evento.fecha.isoformat(),
        lugar=evento.lugar,
        evento_id=identidad_evento(evento) if editable else None,
        editable=editable,
    )


def _simbolo_academico(fecha: FechaAcademica, dia: date) -> SimboloCalendario:
    if fecha.tipo in _TIPOS_CAMBIO_CUATRI:
        tipo = "cambio_cuatrimestre"
    elif fecha.tipo == "festivo":
        tipo = "festivo"
    elif fecha.tipo == "vacaciones":
        tipo = "vacaciones"
    elif fecha.tipo.startswith("semana_examenes"):
        tipo = "semana_examenes"
    else:
        tipo = "periodo"
    return SimboloCalendario(
        tipo=tipo,
        codigo="calendario",
        nombre=fecha.titulo,
        nombre_ingles=fecha.titulo,
        hora="",
        fecha=dia.isoformat(),
        lugar=None,
    )
