from __future__ import annotations

from Servidor.Dominio.DominioEntities.confirmacion import Confirmacion
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_confirmaciones import RepositorioConfirmaciones


class RepositorioConfirmacionesMemoria(RepositorioConfirmaciones):
    def __init__(self):
        self._confirmaciones: dict[str, Confirmacion] = {}

    def guardar(self, confirmacion: Confirmacion) -> Confirmacion:
        self._confirmaciones[confirmacion.token] = confirmacion
        return confirmacion

    def obtener(self, token: str) -> Confirmacion | None:
        return self._confirmaciones.get(token)

    def eliminar(self, token: str) -> None:
        self._confirmaciones.pop(token, None)

    def eliminar_por_email(self, email: str) -> None:
        for token in [clave for clave, item in self._confirmaciones.items() if item.email == email]:
            del self._confirmaciones[token]
