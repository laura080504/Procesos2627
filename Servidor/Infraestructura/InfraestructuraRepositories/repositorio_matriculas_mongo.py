from __future__ import annotations

from Servidor.Infraestructura.base_datos_mongo import BaseDatosMongo
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas import RepositorioMatriculas


class RepositorioMatriculasMongo(RepositorioMatriculas):
    def __init__(self, base_datos: BaseDatosMongo):
        self.base_datos = base_datos

    def obtener_codigos(self, email: str) -> list[str]:
        return list(self.obtener_notas(email))

    def obtener_notas(self, email: str) -> dict[str, float | None]:
        documentos = self.base_datos.coleccion("matricula").find({"email": email}).sort("codigo", 1)
        return {documento["codigo"]: documento.get("nota") for documento in documentos}

    def obtener_convalidadas(self, email: str) -> set[str]:
        documentos = self.base_datos.coleccion("matricula").find(
            {"email": email, "convalidada": True},
            {"codigo": 1},
        )
        return {documento["codigo"] for documento in documentos}

    def reemplazar_alumno(self, email: str, codigos: list[str]) -> None:
        coleccion = self.base_datos.coleccion("matricula")
        coleccion.delete_many({"email": email})
        if codigos:
            coleccion.insert_many(
                [
                    {
                        "_id": f"{email}|{codigo}",
                        "email": email,
                        "codigo": codigo,
                        "nota": None,
                        "convalidada": False,
                    }
                    for codigo in dict.fromkeys(codigos)
                ]
            )

    def rellenar_notas(self, email: str, notas: dict[str, float]) -> None:
        coleccion = self.base_datos.coleccion("matricula")
        for codigo, nota in notas.items():
            coleccion.update_one(
                {
                    "_id": f"{email}|{codigo}",
                    "convalidada": {"$ne": True},
                    "$or": [{"nota": None}, {"nota": {"$exists": False}}],
                },
                {"$set": {"nota": nota}},
            )

    def marcar_convalidadas(self, email: str, codigos: list[str]) -> None:
        coleccion = self.base_datos.coleccion("matricula")
        for codigo in codigos:
            coleccion.update_one(
                {"_id": f"{email}|{codigo}"},
                {
                    "$set": {
                        "email": email,
                        "codigo": codigo,
                        "nota": None,
                        "convalidada": True,
                    }
                },
                upsert=True,
            )
