from __future__ import annotations

from datetime import datetime, timezone

from Servidor.Dominio.DominioEntities.sesion import Sesion
from Servidor.Dominio.DominioServices.token_seguro import hash_token
from Servidor.Infraestructura.base_datos_mongo import BaseDatosMongo
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_sesiones import RepositorioSesiones


class RepositorioSesionesMongo(RepositorioSesiones):
    def __init__(self, base_datos: BaseDatosMongo):
        self.base_datos = base_datos

    def guardar(self, sesion: Sesion) -> Sesion:
        clave = hash_token(sesion.token)
        self.base_datos.coleccion("sesiones").replace_one(
            {"_id": clave},
            {"_id": clave, "email": sesion.email, "expira_en": sesion.expira_en},
            upsert=True,
        )
        return sesion

    def obtener(self, token: str) -> Sesion | None:
        documento = self.base_datos.coleccion("sesiones").find_one({"_id": hash_token(token)})
        if not documento:
            return None
        return Sesion(
            token=token,
            email=documento["email"],
            expira_en=self._a_fecha(documento["expira_en"]),
        )

    def eliminar(self, token: str) -> None:
        self.base_datos.coleccion("sesiones").delete_one({"_id": hash_token(token)})

    def eliminar_por_email(self, email: str) -> None:
        self.base_datos.coleccion("sesiones").delete_many({"email": email})

    def actualizar_email(self, email_actual: str, email_nuevo: str) -> None:
        self.base_datos.coleccion("sesiones").update_many(
            {"email": email_actual},
            {"$set": {"email": email_nuevo}},
        )

    def _a_fecha(self, valor: datetime) -> datetime:
        if valor.tzinfo is None:
            return valor.replace(tzinfo=timezone.utc)
        return valor
