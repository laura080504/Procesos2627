from __future__ import annotations

from Servidor.Dominio.DominioEntities.evento import Evento, identidad_evento
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_eventos import RepositorioEventos


class RepositorioEventosMemoria(RepositorioEventos):
    def __init__(self):
        self._eventos: dict[str, Evento] = {}

    def obtener_todos(self) -> list[Evento]:
        return list(self._eventos.values())

    def obtener_por_id(self, evento_id: str) -> Evento | None:
        return self._eventos.get(evento_id)

    def reemplazar(self, eventos: list[Evento]) -> None:
        self._eventos = {}
        for evento in eventos:
            self.guardar(evento)

    def guardar(self, evento: Evento) -> None:
        con_id = evento.con_id()
        self._eventos[identidad_evento(con_id)] = con_id

    def eliminar(self, evento_id: str) -> bool:
        return self._eventos.pop(evento_id, None) is not None
