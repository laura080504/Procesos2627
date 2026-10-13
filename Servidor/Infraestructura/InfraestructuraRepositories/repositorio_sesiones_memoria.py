from __future__ import annotations

from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_sesiones import RepositorioSesiones
from Servidor.Dominio.DominioEntities.sesion import Sesion


class RepositorioSesionesMemoria(RepositorioSesiones):
    def __init__(self):
        self._sesiones: dict[str, Sesion] = {}

    def guardar(self, sesion: Sesion) -> Sesion:
        self._sesiones[sesion.token] = sesion
        return sesion

    def obtener(self, token: str) -> Sesion | None:
        return self._sesiones.get(token)

    def eliminar(self, token: str) -> None:
        self._sesiones.pop(token, None)

    def eliminar_por_email(self, email: str) -> None:
        for token in [t for t, s in self._sesiones.items() if s.email == email]:
            del self._sesiones[token]

    def actualizar_email(self, email_actual: str, email_nuevo: str) -> None:
        for token, sesion in list(self._sesiones.items()):
            if sesion.email == email_actual:
                self._sesiones[token] = Sesion(
                    token=sesion.token, email=email_nuevo, expira_en=sesion.expira_en
                )
