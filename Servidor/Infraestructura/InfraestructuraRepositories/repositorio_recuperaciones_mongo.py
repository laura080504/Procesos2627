from __future__ import annotations

from datetime import datetime, timezone

from Servidor.Infraestructura.base_datos_mongo import BaseDatosMongo
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_recuperaciones import RepositorioRecuperaciones
from Servidor.Dominio.DominioEntities.recuperacion import Recuperacion


class RepositorioRecuperacionesMongo(RepositorioRecuperaciones):
    def __init__(self, base_datos: BaseDatosMongo):
        self.base_datos = base_datos

    def guardar(self, recuperacion: Recuperacion) -> Recuperacion:
        self.base_datos.coleccion("recuperaciones").replace_one(
            {"_id": recuperacion.token},
            {"_id": recuperacion.token, "email": recuperacion.email, "expira_en": recuperacion.expira_en},
            upsert=True,
        )
        return recuperacion

    def obtener(self, token: str) -> Recuperacion | None:
        documento = self.base_datos.coleccion("recuperaciones").find_one({"_id": token})
        return self._a_recuperacion(documento) if documento else None

    def eliminar(self, token: str) -> None:
        self.base_datos.coleccion("recuperaciones").delete_one({"_id": token})

    def eliminar_por_email(self, email: str) -> None:
        self.base_datos.coleccion("recuperaciones").delete_many({"email": email})

    def _a_recuperacion(self, documento: dict) -> Recuperacion:
        return Recuperacion(
            token=documento["_id"],
            email=documento["email"],
            expira_en=self._a_fecha(documento["expira_en"]),
        )

    def _a_fecha(self, valor: datetime) -> datetime:
        if valor.tzinfo is None:
            return valor.replace(tzinfo=timezone.utc)
        return valor
