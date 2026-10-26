from __future__ import annotations

from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_matriculas import RepositorioMatriculas


class RepositorioMatriculasMemoria(RepositorioMatriculas):
    def __init__(self):
        self._por_email: dict[str, dict[str, float | None]] = {}

    def obtener_codigos(self, email: str) -> list[str]:
        return list(self._por_email.get(email, {}))

    def obtener_notas(self, email: str) -> dict[str, float | None]:
        return dict(self._por_email.get(email, {}))

    def reemplazar_alumno(self, email: str, codigos: list[str]) -> None:
        self._por_email[email] = {codigo: None for codigo in dict.fromkeys(codigos)}

    def rellenar_notas(self, email: str, notas: dict[str, float]) -> None:
        guardadas = self._por_email.setdefault(email, {})
        for codigo, nota in notas.items():
            if codigo in guardadas and guardadas[codigo] is None:
                guardadas[codigo] = nota
