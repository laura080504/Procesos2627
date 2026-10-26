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
        }

    def _a_evento(self, documento: dict) -> Evento:
        return Evento(
            fecha=date.fromisoformat(documento["fecha"]),
            codigo=documento["codigo"],
            tipo=TipoEvento(documento["tipo"]),
        )


def _clave(evento: Evento) -> str:
    return f"{evento.fecha.isoformat()}|{evento.codigo}|{evento.tipo.value}"
