from __future__ import annotations

from Servidor.Infraestructura.base_datos_mongo import BaseDatosMongo
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_docencia import RepositorioDocencia


class RepositorioDocenciaMongo(RepositorioDocencia):
    def __init__(self, base_datos: BaseDatosMongo):
        self.base_datos = base_datos

    def obtener_codigos(self, email: str) -> list[str]:
        documento = self.base_datos.coleccion("docencia").find_one({"_id": email.strip().lower()})
        if not documento:
            return []
        return list(documento.get("codigos") or [])

    def obtener_nombre_docente(self, email: str) -> str | None:
        documento = self.base_datos.coleccion("docencia").find_one(
            {"_id": email.strip().lower()},
            {"nombre_docente": 1},
        )
        valor = (documento or {}).get("nombre_docente")
        return (valor or "").strip() or None

    def reemplazar(
        self,
        email: str,
        codigos: list[str],
        nombre_docente: str | None = None,
    ) -> None:
        clave = email.strip().lower()
        unicos = list(dict.fromkeys(codigo.strip() for codigo in codigos if codigo.strip()))
        campos: dict = {"codigos": unicos, "email": clave}
        if nombre_docente is not None:
            campos["nombre_docente"] = nombre_docente.strip() or None
        self.base_datos.coleccion("docencia").update_one(
            {"_id": clave},
            {"$set": campos},
            upsert=True,
        )

    def cambiar_email(self, email_actual: str, email_nuevo: str) -> None:
        actual = email_actual.strip().lower()
        nuevo = email_nuevo.strip().lower()
        if actual == nuevo:
            return
        coleccion = self.base_datos.coleccion("docencia")
        documento = coleccion.find_one({"_id": actual})
        if not documento:
            return
        documento["_id"] = nuevo
        documento["email"] = nuevo
        coleccion.delete_one({"_id": actual})
        coleccion.replace_one({"_id": nuevo}, documento, upsert=True)
