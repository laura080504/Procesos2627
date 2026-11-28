from __future__ import annotations

from Servidor.Dominio.DominioEntities.sesion import Sesion
from Servidor.Dominio.DominioServices.token_seguro import hash_token
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_sesiones import RepositorioSesiones


class RepositorioSesionesMemoria(RepositorioSesiones):
    def __init__(self):
        self._sesiones: dict[str, Sesion] = {}

    def guardar(self, sesion: Sesion) -> Sesion:
        self._sesiones[hash_token(sesion.token)] = sesion
        return sesion

    def obtener(self, token: str) -> Sesion | None:
        return self._sesiones.get(hash_token(token))

    def eliminar(self, token: str) -> None:
        self._sesiones.pop(hash_token(token), None)

    def eliminar_por_email(self, email: str) -> None:
        for token in [t for t, s in self._sesiones.items() if s.email == email]:
            del self._sesiones[token]

    def actualizar_email(self, email_actual: str, email_nuevo: str) -> None:
        for token, sesion in list(self._sesiones.items()):
            if sesion.email == email_actual:
                self._sesiones[token] = Sesion(
                    token=sesion.token, email=email_nuevo, expira_en=sesion.expira_en
                )
