import random
from datetime import date

from Servidor.Dominio.DominioEntities.asignatura import Asignatura
from Servidor.Dominio.DominioEntities.evento import Evento
from Servidor.Dominio.DominioEnums.tipo_evento import TipoEvento

# Octubre de 2026 se ve al abrir la agenda: varios exámenes el 11 y mezclas en otros días.
_OCTUBRE = (
    (4, "42301", TipoEvento.EXAMEN, "09:00", "Aula 1.1"),
    (7, "42305", TipoEvento.ENTREGA, "23:59", None),
    (11, "42300", TipoEvento.EXAMEN, "09:00", "Aula Multiusos"),
    (11, "42302", TipoEvento.EXAMEN, "11:30", "Aula 2.1"),
    (11, "42310", TipoEvento.EXAMEN, "16:00", "Aula 1.3"),
    (11, "42314", TipoEvento.EXAMEN, "18:00", "Aula 2.2"),
    (11, "42330", TipoEvento.EXAMEN, "12:00", "Aula 3.1"),
    (16, "42319", TipoEvento.EXAMEN, "10:00", "Aula 1.2"),
    (16, "42324", TipoEvento.EXAMEN, "15:30", "Aula 2.3"),
    (16, "42306", TipoEvento.ENTREGA, "23:59", None),
    (21, "42312", TipoEvento.ENTREGA, "14:00", None),
    (21, "42313", TipoEvento.ENTREGA, "23:59", None),
    (21, "42318", TipoEvento.ENTREGA, "18:00", None),
    (27, "42321", TipoEvento.EXAMEN, "09:30", "Aula 1.4"),
    (27, "42315", TipoEvento.ENTREGA, "23:59", None),
    (27, "42308", TipoEvento.ENTREGA, "12:00", None),
)

# Noviembre 2026: avisos de la semana actual y la siguiente para matrículas de demo.
_NOVIEMBRE = (
    (19, "42304", TipoEvento.ENTREGA, "23:59", None),
    (19, "42305", TipoEvento.ENTREGA, "18:00", None),
    (20, "42300", TipoEvento.EXAMEN, "11:00", "Aula Multiusos"),
    (21, "42322", TipoEvento.ENTREGA, "23:59", None),
    (25, "42302", TipoEvento.EXAMEN, "09:30", "Aula 2.1"),
    (26, "42314", TipoEvento.ENTREGA, "23:59", None),
    (26, "42310", TipoEvento.EXAMEN, "16:00", "Aula 1.3"),
    (27, "42301", TipoEvento.ENTREGA, "14:00", None),
)

_HORAS_EXAMEN = ("09:00", "09:30", "11:00", "11:30", "16:00", "18:00")
_HORAS_ENTREGA = ("12:00", "14:00", "18:00", "23:59")
_AULAS = ("Aula 1.1", "Aula 1.2", "Aula 1.3", "Aula 2.1", "Aula 2.2", "Aula Multiusos")


def generar_eventos_muestra(asignaturas: list[Asignatura]) -> list[Evento]:
    codigos = {asignatura.codigo for asignatura in asignaturas}
    eventos = [
        Evento(date(2026, 10, dia), codigo, tipo, hora, lugar)
        for dia, codigo, tipo, hora, lugar in _OCTUBRE
        if codigo in codigos
    ]
    eventos.extend(
        Evento(date(2026, 11, dia), codigo, tipo, hora, lugar)
        for dia, codigo, tipo, hora, lugar in _NOVIEMBRE
        if codigo in codigos
    )
    aleatorio = random.Random(406)
    disponibles = sorted(codigos)
    dias_noviembre_fijos = {dia for dia, *_ in _NOVIEMBRE}
    for anio, mes in ((2026, 11), (2026, 12), (2027, 1), (2027, 5)):
        for dia in aleatorio.sample(range(1, 29), 4):
            if anio == 2026 and mes == 11 and dia in dias_noviembre_fijos:
                continue
            codigo = aleatorio.choice(disponibles)
            tipo = aleatorio.choice((TipoEvento.EXAMEN, TipoEvento.ENTREGA))
            eventos.append(_evento_aleatorio(date(anio, mes, dia), codigo, tipo, aleatorio))
    return eventos


def _evento_aleatorio(fecha: date, codigo: str, tipo: TipoEvento, aleatorio: random.Random) -> Evento:
    if tipo == TipoEvento.EXAMEN:
        return Evento(fecha, codigo, tipo, aleatorio.choice(_HORAS_EXAMEN), aleatorio.choice(_AULAS))
    return Evento(fecha, codigo, tipo, aleatorio.choice(_HORAS_ENTREGA), None)
