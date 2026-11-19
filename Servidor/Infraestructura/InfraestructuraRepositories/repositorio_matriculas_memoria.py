from __future__ import annotations

from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas import RepositorioMatriculas


class RepositorioMatriculasMemoria(RepositorioMatriculas):
    def __init__(self):
        # codigo -> {nota, grupo, convalidada, activa}
        self._filas: dict[str, dict[str, dict]] = {}

    def _filas_de(self, email: str) -> dict[str, dict]:
        return self._filas.setdefault(email, {})

    def obtener_codigos(self, email: str) -> list[str]:
        return [codigo for codigo, fila in self._filas_de(email).items() if fila.get("activa", True)]

    def obtener_notas(self, email: str) -> dict[str, float | None]:
        return {codigo: fila.get("nota") for codigo, fila in self._filas_de(email).items()}

    def obtener_grupos(self, email: str) -> dict[str, str]:
        return {
            codigo: (fila.get("grupo") or "A")
            for codigo, fila in self._filas_de(email).items()
            if fila.get("activa", True)
        }

    def obtener_convalidadas(self, email: str) -> set[str]:
        return {
            codigo
            for codigo, fila in self._filas_de(email).items()
            if fila.get("convalidada")
        }

    def reemplazar_alumno(
        self,
        email: str,
        codigos: list[str],
        grupos: dict[str, str] | None = None,
    ) -> None:
        previas = self._filas_de(email)
        asignados = grupos or {}
        unicos = list(dict.fromkeys(codigos))
        nuevas: dict[str, dict] = {}
        activos = set(unicos)

        for codigo in unicos:
            anterior = previas.get(codigo, {})
            nuevas[codigo] = {
                "nota": anterior.get("nota"),
                "grupo": (asignados.get(codigo) or anterior.get("grupo") or "A").strip() or "A",
                "convalidada": bool(anterior.get("convalidada")),
                "activa": True,
            }

        for codigo, anterior in previas.items():
            if codigo in activos:
                continue
            if anterior.get("nota") is not None or anterior.get("convalidada"):
                nuevas[codigo] = {
                    "nota": anterior.get("nota"),
                    "grupo": anterior.get("grupo") or "A",
                    "convalidada": bool(anterior.get("convalidada")),
                    "activa": False,
                }

        self._filas[email] = nuevas

    def rellenar_notas(self, email: str, notas: dict[str, float]) -> None:
        filas = self._filas_de(email)
        for codigo, nota in notas.items():
            fila = filas.get(codigo)
            if not fila or fila.get("convalidada"):
                continue
            if fila.get("nota") is None:
                fila["nota"] = nota

    def sincronizar_calificaciones(
        self,
        email: str,
        notas: dict[str, float | None],
        convalidadas: set[str] | frozenset[str],
    ) -> None:
        filas = self._filas_de(email)
        marcadas = set(convalidadas)
        calificadas = set(notas) | marcadas
        nuevas: dict[str, dict] = {}

        for codigo, anterior in filas.items():
            activa = bool(anterior.get("activa", True))
            if codigo in calificadas:
                convalidada = codigo in marcadas
                nuevas[codigo] = {
                    "nota": None if convalidada else notas.get(codigo),
                    "grupo": anterior.get("grupo") or "A",
                    "convalidada": convalidada,
                    "activa": activa,
                }
            elif activa:
                nuevas[codigo] = {
                    "nota": None,
                    "grupo": anterior.get("grupo") or "A",
                    "convalidada": False,
                    "activa": True,
                }

        for codigo in calificadas:
            if codigo in nuevas:
                continue
            convalidada = codigo in marcadas
            nuevas[codigo] = {
                "nota": None if convalidada else notas.get(codigo),
                "grupo": "A",
                "convalidada": convalidada,
                "activa": False,
            }

        self._filas[email] = nuevas

    def marcar_convalidadas(self, email: str, codigos: list[str]) -> None:
        filas = self._filas_de(email)
        for codigo in codigos:
            anterior = filas.get(codigo, {})
            filas[codigo] = {
                "nota": None,
                "grupo": anterior.get("grupo") or "A",
                "convalidada": True,
                "activa": bool(anterior.get("activa", True)) if anterior else True,
            }

    def vaciar_todos_excepto(self, email: str) -> None:
        conservar = email.strip().lower()
        for alumno in list(self._filas):
            if alumno != conservar:
                self._filas[alumno] = {}
