from __future__ import annotations

from datetime import datetime, timezone

from Servidor.Infraestructura.base_datos_mongo import BaseDatosMongo
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_sesiones import RepositorioSesiones
from Servidor.Dominio.DominioEntities.sesion import Sesion


class RepositorioSesionesMongo(RepositorioSesiones):
    def __init__(self, base_datos: BaseDatosMongo):
        self.base_datos = base_datos

    def guardar(self, sesion: Sesion) -> Sesion:
        self.base_datos.coleccion("sesiones").replace_one(
            {"_id": sesion.token},
            {"_id": sesion.token, "email": sesion.email, "expira_en": sesion.expira_en},
            upsert=True,
        )
        return sesion

    def obtener(self, token: str) -> Sesion | None:
        documento = self.base_datos.coleccion("sesiones").find_one({"_id": token})
        return self._a_sesion(documento) if documento else None

    def eliminar(self, token: str) -> None:
        self.base_datos.coleccion("sesiones").delete_one({"_id": token})

    def eliminar_por_email(self, email: str) -> None:
        self.base_datos.coleccion("sesiones").delete_many({"email": email})

    def actualizar_email(self, email_actual: str, email_nuevo: str) -> None:
        self.base_datos.coleccion("sesiones").update_many(
            {"email": email_actual},
            {"$set": {"email": email_nuevo}},
        )

    def _a_sesion(self, documento: dict) -> Sesion:
        return Sesion(
            token=documento["_id"],
            email=documento["email"],
            expira_en=self._a_fecha(documento["expira_en"]),
        )

    def _a_fecha(self, valor: datetime) -> datetime:
        if valor.tzinfo is None:
            return valor.replace(tzinfo=timezone.utc)
        return valor
