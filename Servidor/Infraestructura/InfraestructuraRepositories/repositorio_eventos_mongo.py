from __future__ import annotations

from datetime import date

from Servidor.Dominio.DominioEntities.evento import Evento
from Servidor.Dominio.DominioEnums.tipo_evento import TipoEvento
from Servidor.Infraestructura.base_datos_mongo import BaseDatosMongo
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_eventos import RepositorioEventos


class RepositorioEventosMongo(RepositorioEventos):
    def __init__(self, base_datos: BaseDatosMongo):
        self.base_datos = base_datos

    def obtener_todos(self) -> list[Evento]:
        documentos = self.base_datos.coleccion("evento").find()
        return [self._a_evento(documento) for documento in documentos]

    def reemplazar(self, eventos: list[Evento]) -> None:
        coleccion = self.base_datos.coleccion("evento")
        coleccion.delete_many({})
        if eventos:
            coleccion.insert_many([{"_id": _clave(evento), **self._a_documento(evento)} for evento in eventos])

    def _a_documento(self, evento: Evento) -> dict:
        return {
            "fecha": evento.fecha.isoformat(),
            "codigo": evento.codigo,
            "tipo": evento.tipo.value,
            "hora": evento.hora,
            "lugar": evento.lugar,
        }

    def _a_evento(self, documento: dict) -> Evento:
        tipo = TipoEvento(documento["tipo"])
        codigo = documento["codigo"]
        lugar = None
        if tipo == TipoEvento.EXAMEN:
            lugar = documento.get("lugar") or _aula_por_defecto(codigo)
        return Evento(
            fecha=date.fromisoformat(documento["fecha"]),
            codigo=codigo,
            tipo=tipo,
            hora=documento.get("hora") or _hora_por_defecto(codigo, tipo),
            lugar=lugar,
        )


def _hora_por_defecto(codigo: str, tipo: TipoEvento) -> str:
    base = sum(ord(caracter) for caracter in codigo) % 4
    if tipo == TipoEvento.EXAMEN:
        return ("09:00", "11:30", "16:00", "18:00")[base]
    return ("12:00", "14:00", "18:00", "23:59")[base]


def _aula_por_defecto(codigo: str) -> str:
    base = int(codigo[-2:]) if codigo[-2:].isdigit() else 1
    return f"Aula {(base % 3) + 1}.{(base % 4) + 1}"


def _clave(evento: Evento) -> str:
    return f"{evento.fecha.isoformat()}|{evento.codigo}|{evento.tipo.value}"
