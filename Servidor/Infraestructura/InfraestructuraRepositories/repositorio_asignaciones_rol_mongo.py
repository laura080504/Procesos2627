from __future__ import annotations

from datetime import timezone

from Servidor.Dominio.DominioEntities.asignacion_rol import AsignacionRol
from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Infraestructura.base_datos_mongo import BaseDatosMongo
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_asignaciones_rol import (
    RepositorioAsignacionesRol,
)


class RepositorioAsignacionesRolMongo(RepositorioAsignacionesRol):
    def __init__(self, base_datos: BaseDatosMongo):
        self.base_datos = base_datos

    def guardar(self, asignacion: AsignacionRol) -> AsignacionRol:
        self.base_datos.coleccion("asignaciones_rol").replace_one(
            {"_id": asignacion.token},
            {
                "_id": asignacion.token,
                "email": asignacion.email,
                "rol_destino": asignacion.rol_destino.value,
                "expira_en": asignacion.expira_en,
            },
            upsert=True,
        )
        return asignacion

    def obtener(self, token: str) -> AsignacionRol | None:
        documento = self.base_datos.coleccion("asignaciones_rol").find_one({"_id": token})
        if documento is None:
            return None
        expira = documento["expira_en"]
        if getattr(expira, "tzinfo", None) is None:
            expira = expira.replace(tzinfo=timezone.utc)
        return AsignacionRol(
            token=documento["_id"],
            email=documento["email"],
            rol_destino=Rol(documento["rol_destino"]),
            expira_en=expira,
        )

    def eliminar(self, token: str) -> None:
        self.base_datos.coleccion("asignaciones_rol").delete_one({"_id": token})

    def eliminar_por_email(self, email: str) -> None:
        self.base_datos.coleccion("asignaciones_rol").delete_many({"email": email.strip().lower()})
