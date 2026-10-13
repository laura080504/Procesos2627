from __future__ import annotations

from urllib.parse import quote_plus, urlparse, urlunparse

from pymongo import MongoClient
from pymongo.errors import OperationFailure


def uri_con_credenciales(uri: str, usuario: str | None, contrasena: str | None) -> str:
    if not usuario or contrasena is None:
        return uri
    partes = urlparse(uri)
    if partes.username:
        return uri
    host = partes.hostname or ""
    if partes.port:
        host = f"{host}:{partes.port}"
    return urlunparse(partes._replace(netloc=f"{quote_plus(usuario)}:{quote_plus(contrasena)}@{host}"))


class BaseDatosMongo:
    def __init__(
        self,
        uri: str = "",
        nombre: str = "procesos",
        cliente=None,
        usuario: str | None = None,
        contrasena: str | None = None,
    ):
        if cliente is None:
            if not uri:
                raise ValueError("MONGO_URI es obligatorio cuando DATOS_MOTOR es mongo.")
            cliente = MongoClient(
                uri_con_credenciales(uri, usuario, contrasena),
                serverSelectionTimeoutMS=15000,
            )
        self.cliente = cliente
        self.base = cliente[nombre]
        self._asegurar_indices()

    def coleccion(self, nombre: str):
        return self.base[nombre]

    def _asegurar_indices(self) -> None:
        try:
            self.base["sesiones"].create_index("email")
            self.base["recuperaciones"].create_index("email")
            self.base["confirmaciones"].create_index("email")
        except OperationFailure as error:
            if error.code == 8000 or "auth" in str(error).lower():
                raise ValueError(
                    "Atlas rechazó el usuario o la contraseña. "
                    "Revisa MONGO_USUARIO y MONGO_CONTRASENA en el .env."
                ) from error
            raise
