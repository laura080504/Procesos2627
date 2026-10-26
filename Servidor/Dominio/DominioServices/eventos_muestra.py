import random
from datetime import date

from Servidor.Dominio.DominioEntities.asignatura import Asignatura
from Servidor.Dominio.DominioEntities.evento import Evento
from Servidor.Dominio.DominioEnums.tipo_evento import TipoEvento

# Octubre de 2026 se ve al abrir la agenda: varios exámenes el 11 y mezclas en otros días.
_OCTUBRE = (
    (4, "42301", TipoEvento.EXAMEN),
    (7, "42305", TipoEvento.ENTREGA),
    (11, "42300", TipoEvento.EXAMEN),
    (11, "42302", TipoEvento.EXAMEN),
    (11, "42310", TipoEvento.EXAMEN),
    (11, "42314", TipoEvento.EXAMEN),
    (11, "42330", TipoEvento.EXAMEN),
    (16, "42319", TipoEvento.EXAMEN),
    (16, "42324", TipoEvento.EXAMEN),
    (16, "42306", TipoEvento.ENTREGA),
    (21, "42312", TipoEvento.ENTREGA),
    (21, "42313", TipoEvento.ENTREGA),
    (21, "42318", TipoEvento.ENTREGA),
    (27, "42321", TipoEvento.EXAMEN),
    (27, "42315", TipoEvento.ENTREGA),
    (27, "42308", TipoEvento.ENTREGA),
)


def generar_eventos_muestra(asignaturas: list[Asignatura]) -> list[Evento]:
    codigos = {asignatura.codigo for asignatura in asignaturas}
    eventos = [
        Evento(date(2026, 10, dia), codigo, tipo)
        for dia, codigo, tipo in _OCTUBRE
        if codigo in codigos
    ]
    aleatorio = random.Random(406)
    disponibles = sorted(codigos)
    for anio, mes in ((2026, 11), (2026, 12), (2027, 1), (2027, 5)):
        for dia in aleatorio.sample(range(1, 29), 4):
            codigo = aleatorio.choice(disponibles)
            tipo = aleatorio.choice((TipoEvento.EXAMEN, TipoEvento.ENTREGA))
            eventos.append(Evento(date(anio, mes, dia), codigo, tipo))
    return eventos
