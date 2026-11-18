from __future__ import annotations

from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas import RepositorioMatriculas


class RepositorioMatriculasMemoria(RepositorioMatriculas):
    def __init__(self):
        self._notas: dict[str, dict[str, float | None]] = {}
        self._convalidadas: dict[str, set[str]] = {}

    def obtener_codigos(self, email: str) -> list[str]:
        return list(self._notas.get(email, {}))

    def obtener_notas(self, email: str) -> dict[str, float | None]:
        return dict(self._notas.get(email, {}))

    def obtener_convalidadas(self, email: str) -> set[str]:
        return set(self._convalidadas.get(email, set()))

    def reemplazar_alumno(self, email: str, codigos: list[str]) -> None:
        self._notas[email] = {codigo: None for codigo in dict.fromkeys(codigos)}
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
        convalidadas = self._convalidadas.setdefault(email, set())
        for codigo in codigos:
            guardadas.setdefault(codigo, None)
            guardadas[codigo] = None
            convalidadas.add(codigo)
