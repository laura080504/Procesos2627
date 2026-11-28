from __future__ import annotations

from Servidor.Dominio.DominioEntities.aviso_secretaria import AvisoSecretaria
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_avisos_secretaria import (
    RepositorioAvisosSecretaria,
)


class RepositorioAvisosSecretariaMemoria(RepositorioAvisosSecretaria):
    def __init__(self):
        self._avisos: dict[str, AvisoSecretaria] = {}

    def obtener_todos(self) -> list[AvisoSecretaria]:
        return list(self._avisos.values())

    def obtener_por_id(self, aviso_id: str) -> AvisoSecretaria | None:
        return self._avisos.get(aviso_id)

    def guardar(self, aviso: AvisoSecretaria) -> AvisoSecretaria:
        con_id = aviso.con_id()
        assert con_id.id is not None
        self._avisos[con_id.id] = con_id
        return con_id

    def eliminar(self, aviso_id: str) -> bool:
        return self._avisos.pop(aviso_id, None) is not None

    def vacio(self) -> bool:
        return not self._avisos
