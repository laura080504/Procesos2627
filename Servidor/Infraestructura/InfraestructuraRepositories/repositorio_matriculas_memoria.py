from __future__ import annotations

from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas import RepositorioMatriculas


class RepositorioMatriculasMemoria(RepositorioMatriculas):
    def __init__(self):
        self._notas: dict[str, dict[str, float | None]] = {}
        self._grupos: dict[str, dict[str, str]] = {}
        self._convalidadas: dict[str, set[str]] = {}

    def obtener_codigos(self, email: str) -> list[str]:
        return list(self._notas.get(email, {}))

    def obtener_notas(self, email: str) -> dict[str, float | None]:
        return dict(self._notas.get(email, {}))

    def obtener_grupos(self, email: str) -> dict[str, str]:
        return dict(self._grupos.get(email, {}))

    def obtener_convalidadas(self, email: str) -> set[str]:
        return set(self._convalidadas.get(email, set()))

    def reemplazar_alumno(
        self,
        email: str,
        codigos: list[str],
        grupos: dict[str, str] | None = None,
    ) -> None:
        unicos = list(dict.fromkeys(codigos))
        self._notas[email] = {codigo: None for codigo in unicos}
        asignados = grupos or {}
        self._grupos[email] = {
            codigo: (asignados.get(codigo) or "A").strip() or "A" for codigo in unicos
        }
        self._convalidadas[email] = set()

    def rellenar_notas(self, email: str, notas: dict[str, float]) -> None:
        guardadas = self._notas.setdefault(email, {})
        convalidadas = self._convalidadas.setdefault(email, set())
        for codigo, nota in notas.items():
            if codigo in convalidadas:
                continue
            if codigo in guardadas and guardadas[codigo] is None:
                guardadas[codigo] = nota

    def marcar_convalidadas(self, email: str, codigos: list[str]) -> None:
        guardadas = self._notas.setdefault(email, {})
        grupos = self._grupos.setdefault(email, {})
        convalidadas = self._convalidadas.setdefault(email, set())
        for codigo in codigos:
            guardadas.setdefault(codigo, None)
            grupos.setdefault(codigo, "A")
            guardadas[codigo] = None
            convalidadas.add(codigo)

    def vaciar_todos_excepto(self, email: str) -> None:
        conservar = email.strip().lower()
        for alumno in list(self._notas):
            if alumno != conservar:
                self._notas[alumno] = {}
                self._grupos[alumno] = {}
                self._convalidadas[alumno] = set()
