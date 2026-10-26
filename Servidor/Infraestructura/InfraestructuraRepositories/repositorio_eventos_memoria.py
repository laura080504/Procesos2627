from __future__ import annotations

from Servidor.Dominio.DominioEntities.evento import Evento
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_eventos import RepositorioEventos


class RepositorioEventosMemoria(RepositorioEventos):
    def __init__(self):
        self._eventos: dict[str, Evento] = {}

    def obtener_todos(self) -> list[Evento]:
        return list(self._eventos.values())

    def reemplazar(self, eventos: list[Evento]) -> None:
        self._eventos = {_clave(evento): evento for evento in eventos}


def _clave(evento: Evento) -> str:
    return f"{evento.fecha.isoformat()}|{evento.codigo}|{evento.tipo.value}"
