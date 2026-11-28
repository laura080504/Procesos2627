from __future__ import annotations

from Servidor.Infraestructura.base_datos_mongo import BaseDatosMongo
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas import RepositorioMatriculas


class RepositorioMatriculasMongo(RepositorioMatriculas):
    def __init__(self, base_datos: BaseDatosMongo):
        self.base_datos = base_datos
        try:
            self.base_datos.coleccion("matricula").create_index(
                [("email", 1), ("activa", 1), ("meta", 1)],
                name="email_activa_meta",
            )
        except Exception:
            pass

    def obtener_codigos(self, email: str) -> list[str]:
        documentos = (
            self.base_datos.coleccion("matricula")
            .find({"email": email, "activa": {"$ne": False}, "meta": {"$ne": True}}, {"codigo": 1})
            .sort("codigo", 1)
        )
        return [documento["codigo"] for documento in documentos if documento.get("codigo")]

    def obtener_codigos_por_email(self) -> dict[str, list[str]]:
        documentos = self.base_datos.coleccion("matricula").find(
            {"activa": {"$ne": False}, "meta": {"$ne": True}},
            {"email": 1, "codigo": 1},
        )
        por_email: dict[str, list[str]] = {}
        for documento in documentos:
            email = documento.get("email")
            codigo = documento.get("codigo")
            if not email or not codigo:
                continue
            por_email.setdefault(email, []).append(codigo)
        for email, codigos in por_email.items():
            por_email[email] = sorted(set(codigos))
        return por_email

    def obtener_notas(self, email: str) -> dict[str, float | None]:
        documentos = self.base_datos.coleccion("matricula").find(
            {"email": email, "meta": {"$ne": True}}
        ).sort("codigo", 1)
        return {
            documento["codigo"]: documento.get("nota")
            for documento in documentos
            if documento.get("codigo")
        }

    def obtener_grupos(self, email: str) -> dict[str, str]:
        documentos = self.base_datos.coleccion("matricula").find(
            {"email": email, "activa": {"$ne": False}, "meta": {"$ne": True}},
            {"codigo": 1, "grupo": 1},
        )
        return {
            documento["codigo"]: (documento.get("grupo") or "A")
            for documento in documentos
            if documento.get("codigo")
        }

    def obtener_convalidadas(self, email: str) -> set[str]:
        documentos = self.base_datos.coleccion("matricula").find(
            {"email": email, "convalidada": True, "meta": {"$ne": True}},
            {"codigo": 1},
        )
        return {documento["codigo"] for documento in documentos}

    def reemplazar_alumno(
        self,
        email: str,
        codigos: list[str],
        grupos: dict[str, str] | None = None,
    ) -> None:
        coleccion = self.base_datos.coleccion("matricula")
        previas = {
            documento["codigo"]: documento
            for documento in coleccion.find({"email": email, "meta": {"$ne": True}})
            if documento.get("codigo")
        }
        asignados = grupos or {}
        unicos = list(dict.fromkeys(codigos))
        activos = set(unicos)
        coleccion.delete_many({"email": email, "meta": {"$ne": True}})

        documentos = []
        for codigo in unicos:
            anterior = previas.get(codigo, {})
            documentos.append(
                {
                    "_id": f"{email}|{codigo}",
                    "email": email,
                    "codigo": codigo,
                    "grupo": (asignados.get(codigo) or anterior.get("grupo") or "A").strip() or "A",
                    "nota": anterior.get("nota"),
                    "convalidada": bool(anterior.get("convalidada")),
                    "activa": True,
                }
            )

        for codigo, anterior in previas.items():
            if codigo in activos:
                continue
            if anterior.get("nota") is not None or anterior.get("convalidada"):
                documentos.append(
                    {
                        "_id": f"{email}|{codigo}",
                        "email": email,
                        "codigo": codigo,
                        "grupo": (anterior.get("grupo") or "A"),
                        "nota": anterior.get("nota"),
                        "convalidada": bool(anterior.get("convalidada")),
                        "activa": False,
                    }
                )

        if documentos:
            coleccion.insert_many(documentos)

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

    def sincronizar_calificaciones(
        self,
        email: str,
        notas: dict[str, float | None],
        convalidadas: set[str] | frozenset[str],
    ) -> None:
        coleccion = self.base_datos.coleccion("matricula")
        previas = {
            documento["codigo"]: documento
            for documento in coleccion.find({"email": email, "meta": {"$ne": True}})
            if documento.get("codigo")
        }
        marcadas = set(convalidadas)
        calificadas = set(notas) | marcadas
        documentos = []

        for codigo, anterior in previas.items():
            activa = anterior.get("activa", True) is not False
            if codigo in calificadas:
                convalidada = codigo in marcadas
                documentos.append(
                    {
                        "_id": f"{email}|{codigo}",
                        "email": email,
                        "codigo": codigo,
                        "grupo": anterior.get("grupo") or "A",
                        "nota": None if convalidada else notas.get(codigo),
                        "convalidada": convalidada,
                        "activa": activa,
                    }
                )
            elif activa:
                documentos.append(
                    {
                        "_id": f"{email}|{codigo}",
                        "email": email,
                        "codigo": codigo,
                        "grupo": anterior.get("grupo") or "A",
                        "nota": None,
                        "convalidada": False,
                        "activa": True,
                    }
                )

        for codigo in calificadas:
            if any(documento["codigo"] == codigo for documento in documentos):
                continue
            convalidada = codigo in marcadas
            documentos.append(
                {
                    "_id": f"{email}|{codigo}",
                    "email": email,
                    "codigo": codigo,
                    "grupo": "A",
                    "nota": None if convalidada else notas.get(codigo),
                    "convalidada": convalidada,
                    "activa": False,
                }
            )

        coleccion.delete_many({"email": email, "meta": {"$ne": True}})
        if documentos:
            coleccion.insert_many(documentos)

    def obtener_intensificacion(self, email: str) -> str | None:
        documento = self.base_datos.coleccion("matricula").find_one(
            {"_id": f"{email}|_perfil"},
            {"intensificacion": 1},
        )
        valor = (documento or {}).get("intensificacion")
        return (valor or "").strip().lower() or None

    def guardar_intensificacion(self, email: str, intensificacion: str | None) -> None:
        valor = (intensificacion or "").strip().lower() or None
        self.base_datos.coleccion("matricula").update_one(
            {"_id": f"{email}|_perfil"},
            {"$set": {"email": email, "intensificacion": valor, "meta": True}},
            upsert=True,
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
                    },
                    "$setOnInsert": {"grupo": "A", "activa": True},
                },
                upsert=True,
            )

    def cambiar_email(self, email_actual: str, email_nuevo: str) -> None:
        actual = email_actual.strip().lower()
        nuevo = email_nuevo.strip().lower()
        if actual == nuevo:
            return
        coleccion = self.base_datos.coleccion("matricula")
        documentos = list(coleccion.find({"email": actual}))
        if not documentos:
            return
        coleccion.delete_many({"email": actual})
        for documento in documentos:
            identificador = documento.get("_id")
            sufijo = ""
            if isinstance(identificador, str) and "|" in identificador:
                sufijo = identificador.split("|", 1)[1]
            documento["email"] = nuevo
            documento["_id"] = f"{nuevo}|{sufijo}" if sufijo else f"{nuevo}|{identificador}"
            coleccion.replace_one({"_id": documento["_id"]}, documento, upsert=True)

    def vaciar_todos_excepto(self, email: str) -> None:
        self.base_datos.coleccion("matricula").delete_many({"email": {"$ne": email.strip().lower()}})
