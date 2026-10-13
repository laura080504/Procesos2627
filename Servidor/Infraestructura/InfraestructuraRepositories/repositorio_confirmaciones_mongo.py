from __future__ import annotations

from datetime import datetime, timezone

from Servidor.Dominio.DominioEntities.confirmacion import Confirmacion
from Servidor.Infraestructura.base_datos_mongo import BaseDatosMongo
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_confirmaciones import RepositorioConfirmaciones


class RepositorioConfirmacionesMongo(RepositorioConfirmaciones):
    def __init__(self, base_datos: BaseDatosMongo):
        self.base_datos = base_datos

    def guardar(self, confirmacion: Confirmacion) -> Confirmacion:
        self.base_datos.coleccion("confirmaciones").replace_one(
            {"_id": confirmacion.token},
            {"_id": confirmacion.token, "email": confirmacion.email, "expira_en": confirmacion.expira_en},
            upsert=True,
        )
        return confirmacion

    def obtener(self, token: str) -> Confirmacion | None:
        documento = self.base_datos.coleccion("confirmaciones").find_one({"_id": token})
        return self._a_confirmacion(documento) if documento else None

    def eliminar(self, token: str) -> None:
        self.base_datos.coleccion("confirmaciones").delete_one({"_id": token})

    def eliminar_por_email(self, email: str) -> None:
        self.base_datos.coleccion("confirmaciones").delete_many({"email": email})

    def _a_confirmacion(self, documento: dict) -> Confirmacion:
        return Confirmacion(
            token=documento["_id"],
            email=documento["email"],
            expira_en=self._a_fecha(documento["expira_en"]),
        )

    def _a_fecha(self, valor: datetime) -> datetime:
        if valor.tzinfo is None:
            return valor.replace(tzinfo=timezone.utc)
        return valor
